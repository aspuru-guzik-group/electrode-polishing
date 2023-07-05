from serial import Serial
import struct
import random


pulses0 = [
    [0,0,0,0],
    [1,1,440,440],
    [0,0,440,440],

    [1, 1, 440, 466],
    [0, 0, 440, 466],

    [1, 1, 440, 493],
    [0, 0, 440, 493],

    [1, 1, 440, 523],
    [0, 0, 440, 523],

    [1, 1, 440, 554],
    [0, 0, 440, 554],

    [1, 1, 440, 587],
    [0, 0, 440, 587],

    [1, 1, 440, 622],
    [0, 0, 440, 622],

    [1, 1, 440, 659],
    [0, 0, 440, 659],

    [1, 1, 440, 698],
    [0, 0, 440, 698],

    [1, 1, 440, 739],
    [0, 0, 440, 739],

    [1, 1, 440, 783],
    [0, 0, 440, 783],

    [1, 1, 440, 830],
    [0, 0, 440, 830],

    [1, 1, 440, 880],
    [0, 0, 440, 880],

    # [0,0,493,493],
    # [0,1,4000, 300],
    # [1,0,4000,300]
]

# dev = Serial(port = "COM3", baudrate=9600, timeout=2)

def run_slider(pulses):
    with Serial(port = "COM3", baudrate=9600, timeout=2) as dev:
        for pulse in pulses:
            cmd = struct.pack('>bbhh', pulse[0], pulse[1], pulse[2], pulse[3])
            dev.write(cmd)
            rtn = dev.read()
            print(rtn)


pulses = [[0,0,0,0]]
x0 = 0
y0 = 0
for i in range (0, 20):
    delta_x = random.randint(1, 2000)
    delta_y = random.randint(1, 2000)
    if x0 + delta_x > 5000:
        x_dir = 0
    elif x0 + delta_x < -5000:
        x_dir = 1
    else:
        x_dir = random.randint(0, 1)
    if y0 + delta_y > 5000:
        y_dir = 0
    elif y0 + delta_y < -5000:
        y_dir = 1
    else:
        y_dir = random.randint(0, 1)
    if x_dir == 0:
        x0 -= delta_x
    else:
        x0 += delta_x
    if y_dir == 0:
        y0 -= delta_y
    else:
        y0 += delta_y
    pulses.append([x_dir, y_dir, delta_x, delta_y])

print(pulses)

run_slider(pulses=pulses)


# run_slider(pulses=[[0,0,0,0],[1, 1, 500, 200]])
