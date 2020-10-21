import sys
from lx16a import LX16A
import time
import math
import random
import numpy as np

LX16A.initialize("/dev/ttyUSB2")
# initialize two motors
servo11 = LX16A(11)
servo12 = LX16A(12)
servo13 = LX16A(13)
servo21 = LX16A(21)
servo22 = LX16A(22)
servo23 = LX16A(23)

servo11.servoMode()
servo12.servoMode()
servo13.servoMode()
servo21.servoMode()
servo22.servoMode()
servo23.servoMode()

class Servo_ctrl(object):
  def __init__(self, st_value, ed_value, servo_num): 

    self.init_pos = st_value
    self.servo_control = servo_num
    
    self.start_value = st_value
    self.end_value = ed_value
    self.motor_range = ed_value - st_value

  def go(self,to_value):

    input_motor = np.abs(to_value*self.motor_range + self.start_value)

    self.servo_control.moveTimeWrite(int(input_motor))



def servo_limited(s_list):
    for i in range(len(s_list)):
        print(s_list[i].angleLimitRead())


def initialize():

    r_shank.go(0.2)
    r_thigh.go(0)
    r_hip.go(0.5)
    l_shank.go(0.2)
    l_thigh.go(0)
    l_hip.go(0.5)
    time.sleep(2)

def standup():
    l_hip.go(0.8)
    r_hip.go(0.8)
    for i in range(100):
        r_shank.go(0.2+np.sin(2*math.pi*i/800))
        l_shank.go(np.sin(2*math.pi*i/800))
        r_thigh.go(np.sin(2*math.pi*i/800))
        l_thigh.go(0.2+np.sin(2*math.pi*i/800))
        time.sleep(0.04)
    l_hip.go(0.5)
    r_hip.go(0.5)

def walking():

    r_shank.go(0.5)
    r_thigh.go(0.5)
    r_hip.go(0.5)
    l_shank.go(0.5)
    l_thigh.go(0.5)
    l_hip.go(0.5)
    time.sleep(2)

    r_hip.go(0.3)
    l_hip.go(0.3)
    for i in range(10000):
      r_shank.go(0.5+0.2*np.sin(2*math.pi*i/100+0.01*math.pi))
      l_shank.go(0.5-0.2*np.sin(2*math.pi*i/100+0.01*math.pi))
      r_thigh.go(0.5+0.2*np.sin(2*math.pi*i/100))
      l_thigh.go(0.5-0.2*np.sin(2*math.pi*i/100))
      # time.sleep(0.01)

def shaking():
  r_shank.go(0.5)
  l_shank.go(0.5)
  r_thigh.go(0.5)
  l_thigh.go(0.5)
  for i in range(10000):
    r_hip.go(0.6+0.4*np.sin(2*math.pi*i/400))
    l_hip.go(0.6-0.4*np.sin(2*math.pi*i/400))
    time.sleep(0.01)

r_shank = Servo_ctrl(352,160,servo11)
r_thigh = Servo_ctrl(800 ,560,servo12)
r_hip = Servo_ctrl(437,563 ,servo13)
l_shank = Servo_ctrl(125,317,servo21)
l_thigh = Servo_ctrl(273,513,servo22)
l_hip = Servo_ctrl(563,437,servo23)

if __name__ == "__main__":

  # print servo limitation
    s_list = [servo11,servo12,servo13,servo21,servo22,servo23]
    for i in range(len(s_list)):
      print(s_list[i].angleLimitRead())
    initialize()
    walking()
    # shaking()
    # 
    # standup()
    time.sleep(2)


    t = 0
    while True:
        break
        time.sleep(0.04)

        t+=2






