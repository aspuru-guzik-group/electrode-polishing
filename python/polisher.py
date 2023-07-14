from serial import Serial
import struct
import random
import time
import numpy as np


class Polisher(object):
    def __init__(self):
        self.dev = Serial(port="COM3", baudrate=115200, timeout=1)
        self.dev.close()

    def gen_pulses(self):
        pass

    def run_slider(self, pulses):
        self.dev.timeout = 1
        self.dev.open()
        for pulse in pulses:
            cmd = struct.pack('>bbbhh', 0x01, pulse[0], pulse[1], pulse[2], pulse[3])
            self.dev.write(cmd)
            rtn = self.dev.read()
            #if rtn != b'\x00':
            #    print("Slider move communication error.")
        self.dev.close()
        self.dev.timeout = 1

    def home_slider(self):
        self.dev.timeout = 600
        self.dev.open()
        self.dev.write(b'\x02')
        rtn = self.dev.read()
        if rtn != b'\x00':
            print("Slider home error.")
        self.dev.close()
        self.dev.timeout = 1

    def measure_distance(self, ord_distance: int):
        self.dev.timeout = 5
        self.dev.open()
        cmd = struct.pack('>bb', 0x05, ord_distance)
        time.sleep(2)
        self.dev.write(cmd)
        # time.sleep(1)
        rtn = self.dev.read()
        self.dev.close()
        self.dev.timeout = 1
        distance = struct.unpack('>b', rtn)[0]
        print(distance)

    def measure_voltage(self):
        self.dev.timeout = 5
        self.dev.open()
        cmd = b'\x06'
        time.sleep(2)
        self.dev.write(cmd)
        # time.sleep(1)
        rtn = self.dev.read(2)
        self.dev.close()
        self.dev.timeout = 1
        voltage = struct.unpack('>h', rtn)[0]
        print(voltage)


p = Polisher()
#cur_x = 0
#cur_y = 0
#def goto_pose(goal_x, goal_y):
#    global cur_x, cur_y
#    if cur_x >= goal_x:
#        dir_x = 0
#    else:
#        dir_x = 1
#    if cur_y >= goal_y:
#        dir_y = 0
#    else:
#        dir_y = 1
#    pulse = [dir_y, dir_x, abs(goal_y - cur_y), abs(goal_x - cur_x)]
#    cur_x = goal_x
#    cur_y = goal_y
#    return pulse

## pulses = [[0, 1, 0, 1000]] # slider left (pen right)
## pulses = [[0, 0, 0, 1000]] # slider right (pen left)
## pulses = [[0, 0, 1000, 0]] # slider up (pen down)
## pulses = [[1, 0, 1000, 0]] # slider down (pen up)


#x = 0
#y = 0
#r = 2000
#pulses = [[0,0,0,0]]
#N = 32

#for i in range(N+1):
#    t = 2 * np.pi * i / N
#    gx = int(-r * np.sin(t))
#    gy = int(r * (1.0 - np.cos(t)))
#    print(gx, gy)
#    pulse = goto_pose(gx, gy)
#    pulses.append(pulse)
#    x = gx
#    y = gy

#for i in range(N+1):
#    t = 2 * np.pi * i / N
#    gx = int(-r * np.sin(t))
#    gy = int(r * (np.cos(t) - 1.0))
#    print(gx, gy)
#    pulse = goto_pose(gx, gy)
#    pulses.append(pulse)
#    x = gx
#    y = gy

#print(pulses)
#p.measure_distance(0)
#p.measure_voltage()

#p.home_slider()
#p.run_slider(pulses)

#p.measure_distance(0)
#p.measure_distance(1)

p.measure_voltage()