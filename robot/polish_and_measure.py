import datetime
import logging
import struct
import time

import numpy as np
import rospy
import serial
import websocket
from std_msgs.msg import String
from tqdm import tqdm

from frankapy import FrankaArm


class Slider():
    """
    Slider class with serial connection over Arduino.
    """
    serial_port = None
    baudrate = None
    status = None
    serial = None
    timeout = None

    def __init__(self, serial_port='/dev/ttyACM0', baudrate=115200, timeout=20):
        """
        Initalize Slider class with serial port and baudrate.
        The rest of the parameters such as parity are determined automatically
        
        :serial_port: Port for serial connection (COM1 or /dev/ttyACM0 or etc.)
        :baudrate: Baudrate for serial connection
        Note: connect() function should be called to initiate connection.
        """
        self.serial_port = serial_port
        self.baudrate = baudrate
        self.timeout = timeout
        self.status = 'Disconnected'
    
    def connect(self):
        """
        Initiate serial connection to Arduino.
        Creates a new connection regardless of the current status.
        """
        try:
            self.serial = serial.Serial(port=self.serial_port, baudrate=self.baudrate, timeout=self.timeout);
            response = self.serial.readline().decode("ascii").strip()
            if response == "Ready":
                logging.info('Connected to the slider.')
                return True
            else:
                logging.critical(f'Unexpected welcome message received: {response}')
                return False
        except:
            logging.critical('Could not connect to slider')
            return False
    
    def disconnect(self):
        """
        Disconnect if a serial connection exists
        """
        try:
            self.serial.close()
        except:
            pass
        logging.info('Disconnected from the slider.')
        return True
    
    
    def run_batch(self,pulses):
        
        batch_size = 63; #we have fixed 252 byte frame corresponding to 63 movement commands
        #each command is 4 bytes
        
        #pad with empty commands if necessary
        div, rem = np.divmod(len(pulses),batch_size)
        if rem > 0:
            pad_size = batch_size - rem
            padding = np.zeros((pad_size,4),np.int16)
            pulses.extend(padding.tolist())
            
        #send each chunk of batch of commands
        for i in range(0,(len(pulses) - batch_size) + 1,batch_size):
            batch = bytearray()
            batch.extend('M'.encode('ascii')) #the message starts with M for movement command
            for j in range(i,i+batch_size):
                batch.extend(np.int16(pulses[j][1] * pulses[j][3]).tobytes())
                batch.extend(np.int16(pulses[j][0] * pulses[j][2]).tobytes())
            self.serial.write(batch)
            self.serial.flushOutput()
            response = self.serial.readline()
            response = response.decode('ascii').strip()
            if response != "Batch Completed":
                logging.critical("Slider failed to finish a batch command.")
                return False
        
        logging.info('Slider finished the batch job.')
        return True
    
    def reset_slider(self):
        self.serial.write('R'.encode('ascii')) #the message is only "R" for position resetting command
        self.serial.flushOutput()
        response = self.serial.readline()
        response = response.decode('ascii').strip()
        if response != "Homing Completed":
            logging.critical("Slider failed to finish a homing command.")
            return False
    
        logging.info('Slider finished homing.')
        return True

def calculate_pulses():
    x = 0
    y = 0
    r = 4000
    pulses = []
    N = 32

    cx = 0
    cy = 0

    def goto_pose(goal_x, goal_y, cur_x, cur_y):
        if cur_x >= goal_x:
            dir_x = -1
        else:
            dir_x = 1
        if cur_y >= goal_y:
            dir_y = -1
        else:
            dir_y = 1
        pulse = [dir_y, dir_x, abs(goal_y - cur_y), abs(goal_x - cur_x)]
        return pulse

    for i in range(N+1):
        t = 2 * np.pi * i / N
        gx = int(-r * np.sin(t))
        gy = int(r * (1.0 - np.cos(t)))
        pulse = goto_pose(gx, gy, cx, cy)
        pulses.append(pulse)
        cx = gx
        cy = gy

    return pulses

def on_message(ws, message):
    print(message)
    if message == 'Done':
        ws.close()

def on_error(ws, error):
    print(error)

def on_close(ws, close_status_code, close_msg):
    print("### closed ###")

def on_open(ws):
    print("Opened connection")

if __name__ == "__main__":
    logging.getLogger().setLevel(level=logging.INFO)
    pulses = calculate_pulses()
    slider = Slider()
    slider.connect()
    #slider.reset_slider()

    fa = FrankaArm(with_gripper=False)
    fa.reset_joints()
    ee_pose = fa.get_pose()

    pub = rospy.Publisher('scale_service', String, queue_size=10, latch=True)
    total_time = 0
    for i in range(10):
        ee_pose.translation[0] = 0.34
        ee_pose.translation[1] = -0.165
        ee_pose.translation[2] = 0.23
        fa.goto_pose(ee_pose, duration=5, use_impedance=False)

        ee_pose.translation[2] = 0.145
        fa.goto_pose(ee_pose, duration=5, use_impedance=False)

        time.sleep(3)

        start = datetime.datetime.now()
        print(start.isoformat())
        for _ in tqdm(range(50)):
            slider.run_batch(pulses)
        end = datetime.datetime.now()
        print(end.isoformat())
        duration = end - start
        total_time += duration.total_seconds()
        print("total polishing time:", total_time)

        ee_pose.translation[2] = 0.25
        fa.goto_pose(ee_pose, duration=5, use_impedance=False)

        # Washing
        ee_pose.translation[0] = 0.54
        ee_pose.translation[1] = 0.11
        ee_pose.translation[2] = 0.20
        fa.goto_pose(ee_pose, duration=5, use_impedance=False)

        ee_pose.translation[2] = 0.135
        fa.goto_pose(ee_pose, duration=3, use_impedance=False)

        pub.publish("stir,400,15")
        time.sleep(20)

        ee_pose.translation[2] = 0.20
        fa.goto_pose(ee_pose, duration=5, use_impedance=False)
        
        # Measurement
        ee_pose.translation[0] = 0.54
        ee_pose.translation[1] = 0.21
        ee_pose.translation[2] = 0.15
        fa.goto_pose(ee_pose, duration=5, use_impedance=False)

        ee_pose.translation[2] = 0.04
        fa.goto_pose(ee_pose, duration=3, use_impedance=False)

        ws = websocket.WebSocketApp("ws://127.0.0.1:13254/",
                                    on_message=on_message,
                                    on_open=on_open,
                                    on_error=on_error,
                                    on_close=on_close)
        ws.run_forever()
        time.sleep(3)
        
        ee_pose.translation[2] = 0.15
        fa.goto_pose(ee_pose, duration=5, use_impedance=False)

        # Washing again
        ee_pose.translation[0] = 0.54
        ee_pose.translation[1] = 0.11
        ee_pose.translation[2] = 0.20
        fa.goto_pose(ee_pose, duration=5, use_impedance=False)

        ee_pose.translation[2] = 0.135
        fa.goto_pose(ee_pose, duration=3, use_impedance=False)

        pub.publish("stir,400,5")
        time.sleep(10)

        ee_pose.translation[2] = 0.20
        fa.goto_pose(ee_pose, duration=5, use_impedance=False)

    fa.reset_joints()
    slider.disconnect()
time.sleep(10)
