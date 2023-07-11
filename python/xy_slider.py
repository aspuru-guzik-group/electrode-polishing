from serial import Serial
import struct
import time
import numpy as np


def run_slider(pulses):
    with Serial(port = "/dev/ttyACM0", baudrate=9600, timeout=2) as dev:
        # This is necessary to start actual communication.
        dev.write("")
        dev.read()
        for pulse in pulses:
            cmd = struct.pack('>bbhh', pulse[0], pulse[1], pulse[2], pulse[3])
            dev.write(cmd)
            while dev.inWaiting() == 0:
                time.sleep(0.1)
            rtn = dev.readline()
            print("Received: {}".format(rtn))


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

print(pulses)

run_slider(pulses=pulses)
