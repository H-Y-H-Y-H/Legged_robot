import numpy as np
import time
from ctypes import *
lib = CDLL("./lx16a.so")

for i in range(1,13):
    lib.setServoMode(i)

hip_joint = [1,4,7,10]
mid_joint = [2,5,8,11]
end_joint = [3,6,9,12]
origin = 500

class Controller():
    def __init__(self,motor_index, min, max):
        self.min = min
        self.max = max
        self.range = max - min 
        self.i = motor_index

    def act(self, value):
        value = value/2+0.5
        output = int(value * self.range + self.min)
        print(lib.posRead(self.i))
        lib.move(self.i, output, 350)

        print(self.i, output)


Controller_list = [0]*13
for i in range(1,13):
    Controller_list[i]=Controller(i,120,880)



def re_set():
    for i in end_joint:
        lib.move(i, 500,1000)
    for i in hip_joint:
        lib.move(i, 500,1000)
    for i in mid_joint:
        lib.move(i, 500,1000)
    time.sleep(3)
    for i in end_joint:
        lib.move(i, 820,1000)
    time.sleep(3)
    for i in mid_joint:
        lib.move(i, 180,1000)
    time.sleep(1)

def start():
    for i in hip_joint:
        lib.move(i, 500,1000)
    for i in end_joint:
        lib.move(i, 820,1000)
    for i in mid_joint:
        lib.move(i, 180,1000)
    time.sleep(3)

def sin_move(ti, para):
    # print(para)
    action = np.zeros(12)

    action[0] = para[0] * np.sin(ti / 8 * 2 * np.pi + para[2]) + para[10]
    action[3] = para[1] * np.sin(ti / 8 * 2 * np.pi + para[3]) + para[11]
    action[6] = para[1] * np.sin(ti / 8 * 2 * np.pi + para[4]) - para[11]
    action[9] = para[0] * np.sin(ti / 8 * 2 * np.pi + para[5]) - para[10]

    action[1] = -(para[6] * np.sin(ti / 8 * 2 * np.pi + para[2]) + 0.8)
    action[4] = -(para[7] * np.sin(ti / 8 * 2 * np.pi + para[3]) + 0.8)
    action[7] = -(para[7] * np.sin(ti / 8 * 2 * np.pi + para[4]) + 0.8)
    action[10]= -(para[6] * np.sin(ti / 8 * 2 * np.pi + para[5]) + 0.8)

    action[2] = -(para[8] * np.sin(ti / 8 * 2 * np.pi + para[2]) - 0.8)
    action[5] = -(para[9] * np.sin(ti / 8 * 2 * np.pi + para[3]) - 0.8)
    action[8] = -(para[9] * np.sin(ti / 8 * 2 * np.pi + para[4]) - 0.8)
    action[11]= -(para[8] * np.sin(ti / 8 * 2 * np.pi + para[5]) - 0.8)

    


    return  action






    
