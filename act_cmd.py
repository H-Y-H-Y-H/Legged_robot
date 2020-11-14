import sys
from lx16a import LX16A
import time
import math
import random
import numpy as np
from IK import *
from imu import *

LX16A.initialize("/dev/ttyUSB0")
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

    action_l = norm(IK_left(-53.5,-25,-140.27))
    action_r = norm(IK_right(53.5,-25,-140.27))
    do_action(action_r + action_l)
    time.sleep(2)


def standup():
    for i in range(100):
      start_z = -145.27
      target_z = -210
      action_l = norm(IK_left(-73.5,-30,(target_z-start_z)*abs(np.sin(i/200*np.pi))+start_z))
      action_r = norm(IK_right(73.5,-30,(target_z-start_z)*abs(np.sin(i/200*np.pi))+start_z))
      do_action(action_r + action_l)
      time.sleep(0.01)
    
    


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

def do_action(angle_list):

  r_hip.go(1-angle_list[0])
  l_hip.go(angle_list[3])
  r_thigh.go(1-angle_list[1])
  l_thigh.go(1-angle_list[4])
  r_shank.go(angle_list[2])
  l_shank.go(angle_list[5])

def bounce():

  target_z = -190
  step = 25
  refine = 10

  angle_hip_modify = 0
  for i in range(201):

    flip = step*np.sin(2*np.pi*i/refine)
    hip_rotate = angle_hip_modify * np.sin(2*np.pi*i/refine)
    # print("t",IK_right(43.5,-25,target_z-flip),IK_left(-43.5,-25,target_z+flip))
    action_r = norm(IK_right(63.5-hip_rotate,-30,target_z-flip))

    action_l = norm(IK_left(-63.5-hip_rotate,-30,target_z+flip))
    # print(action_r + action_l)
    do_action(action_r + action_l)
    time.sleep(.05)

  

if __name__ == "__main__":
  initialize()
  time.sleep(1)


  gain_h = 0.8
  start_z = -145.27
  target_z = -190
  target_z_l = target_z
  target_z_r = target_z

  motivate_r = 0
  motivate_l = 0
  time_former = time.time()

  standup()
  bounce()
  # time.sleep(2)
  # for i in range(1,11):
  #   action_r = norm(IK_right(73.5,-30,20/10*i-210))
  #   action_l = norm(IK_left(-73.5,-30,20/10*i-210))
  #   time.sleep(0.02)
  #   do_action(action_r + action_l)

  # time.sleep(2)
  # for i in range(10000): 
  #   data = output(time_former)
  #   if i >200:
  #     if data[1]<= -2:
  #       motivate_r+=1
  #       motivate_l-=1
  #       if motivate_r>=2:
  #         motivate_l = 0
  #         motivate_r = 0
  #         if target_z_l == target_z:
  #           target_z_r += gain_h
  #         else:
  #            target_z_l -= gain_h
  #         balance(target_z_r,target_z_l)

  #     elif data[1]>= 2:
  #       motivate_l+=1
  #       motivate_r-=1
  #       if motivate_l>=2:
  #         motivate_l = 0
  #         motivate_r = 0
  #         if target_z_r == target_z:
  #           target_z_l += gain_h
  #         else:
  #           target_z_r -= gain_h
  #         balance(target_z_r,target_z_l)


  #     print(data[1])

  #   time_former = time.time() 

    









  # print servo limitation
    # s_list = [servo11,servo12,servo13,servo21,servo22,servo23]
    # for i in range(len(s_list)):
    #   print(s_list[i].angleLimitRead())

    # initialize()
    # standup()
   
    # walking()
    # shaking()
    # bounce()

    # time_former = time.time()
    # for i in range(10000):
    #     data,time_former = output(time_former)
    #     if i%100 == 0:
    #         print(data)

  # target_z = -190
  # step = 20
  # refine = 10

  # angle_hip_modify = 0
  # for i in range(201):

  #   flip = step*np.sin(2*np.pi*i/refine)
  #   hip_rotate = angle_hip_modify * np.sin(2*np.pi*i/refine)
  #   # print("t",IK_right(43.5,-25,target_z-flip),IK_left(-43.5,-25,target_z+flip))
  #   action_r = norm(IK_right(53.5-hip_rotate,-30,target_z-flip))

  #   action_l = norm(IK_left(-53.5-hip_rotate,-30,target_z+flip))
  #   # print(action_r + action_l)
  #   do_action(action_r + action_l)
  #   time.sleep(.2)

  # print(servo23.angleOffsetWrite())
  # print(servo23.angleOffsetRead())





    # t = 0
    # while True:
    #     break
    #     time.sleep(0.04)

    #     t+=2






