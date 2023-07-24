import serial
from time import sleep
import logging
import numpy as np


class Slider():
    """
    Slider class with serial connection over Arduino.
    """
    serial_port = None
    baudrate = None
    status = None
    serial = None
    timeout = None

    def __init__(self,serial_port='/dev/ttyACM0',baudrate=115200,timeout=20):
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
            self.serial = serial.Serial(port=self.serial_port,baudrate=self.baudrate,timeout=self.timeout);
            sleep(3)
            logging.info('Connected to the slider.')
            return True
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

#Test with generated pattern
if __name__ == "__main__":
    logging.getLogger().setLevel(level=logging.INFO)
    
    cur_x = 0
    cur_y = 0
    def goto_pose(goal_x, goal_y):
        global cur_x, cur_y
        if cur_x >= goal_x:
            dir_x = -1
        else:
            dir_x = 1
        if cur_y >= goal_y:
            dir_y = -1
        else:
            dir_y = 1
        pulse = [dir_y, dir_x, abs(goal_y - cur_y), abs(goal_x - cur_x)]
        cur_x = goal_x
        cur_y = goal_y
        return pulse
    
    # pulses = [[0, 1, 0, 1000]] # slider left (pen right)
    # pulses = [[0, 0, 0, 1000]] # slider right (pen left)
    # pulses = [[0, 0, 1000, 0]] # slider up (pen down)
    # pulses = [[1, 0, 1000, 0]] # slider down (pen up)
    
    x = 0
    y = 0
    r = 2000
    pulses = []
    N = 32
    
    for i in range(N+1):
        t = 2 * np.pi * i / N
        gx = int(-r * np.sin(t))
        gy = int(r * (1.0 - np.cos(t)))
        print(gx, gy)
        pulse = goto_pose(gx, gy)
        pulses.append(pulse)
        x = gx
        y = gy
    
    for i in range(N+1):
        t = 2 * np.pi * i / N
        gx = int(-r * np.sin(t))
        gy = int(r * (np.cos(t) - 1.0))
        print(gx, gy)
        pulse = goto_pose(gx, gy)
        pulses.append(pulse)
        x = gx 
        y = gy

    slider = Slider()
    slider.connect()
    slider.reset_slider()
    slider.run_batch(pulses)
    slider.reset_slider()
    slider.disconnect()
