from frankapy import FrankaArm
import time
from serial import Serial
import numpy as np
import struct

class Polisher(object):
    def __init__(self):
        self.dev = Serial(port="/dev/ttyACM0", baudrate=115200, timeout=1)
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


p = Polisher()
cur_x = 0
cur_y = 0
def goto_pose(goal_x, goal_y):
    global cur_x, cur_y
    if cur_x >= goal_x:
        dir_x = 0
    else:
        dir_x = 1
    if cur_y >= goal_y:
        dir_y = 0
    else:
        dir_y = 1
    pulse = [dir_y, dir_x, abs(goal_y - cur_y), abs(goal_x - cur_x)]
    cur_x = goal_x
    cur_y = goal_y
    return pulse

x = 0
y = 0
r = 2000
pulses = [[0,0,0,0]]
N = 32

for i in range(N+1):
    t = 2 * np.pi * i / N
    gx = int(-r * np.sin(t))
    gy = int(r * (1.0 - np.cos(t)))
    pulse = goto_pose(gx, gy)
    pulses.append(pulse)
    x = gx
    y = gy

for i in range(N+1):
    t = 2 * np.pi * i / N
    gx = int(-r * np.sin(t))
    gy = int(r * (np.cos(t) - 1.0))
    pulse = goto_pose(gx, gy)
    pulses.append(pulse)
    x = gx
    y = gy


if __name__ == "__main__":
    fa = FrankaArm(with_gripper=False)

    fa.reset_joints()

    ee_pose = fa.get_pose()
    ee_pose.translation[0] = 0.33
    ee_pose.translation[1] = 0.12
    ee_pose.translation[2] = 0.25
    fa.goto_pose(ee_pose, duration=10, use_impedance=False)

    ee_pose.translation[2] = 0.15
    fa.goto_pose(ee_pose, duration=5, use_impedance=False)

    p.run_slider(pulses)

    time.sleep(3)

    ee_pose.translation[2] = 0.25
    fa.goto_pose(ee_pose, duration=5, use_impedance=False)

    fa.reset_joints()
