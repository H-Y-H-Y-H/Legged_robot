import numpy as np 
import time

def IK_left(x,y,z):
    
    theta_h = np.arctan2((53.5+x),(21.5+z)) * 180 / np.pi
    if theta_h<-90:
        theta_h+=180
    else:
        theta_h-=180

    a = (14+y)/100
    b = (21.5+z)/-(np.cos(theta_h/180*np.pi)*100)

    value = 16*b*b-16*(a*a+b*b-4*a*a/(a*a+b*b))
    theta_sin_s_1 = (4*b+np.sqrt(value))/8
    theta_sin_t_1 = b - theta_sin_s_1
    theta_s_1 = np.arcsin(theta_sin_s_1)/np.pi*180
    theta_t_1 = np.arcsin(theta_sin_t_1)/np.pi*180


    theta_sin_s_2 = (4*b-np.sqrt(value))/8
    theta_sin_t_2 = b - theta_sin_s_2
    theta_s_2 = np.arcsin(theta_sin_s_2)/np.pi*180
    theta_t_2 = np.arcsin(theta_sin_t_2)/np.pi*180

    prove1 = np.cos(theta_s_1/180*np.pi)+np.cos((180-theta_t_1)/180*np.pi)
    prove2 = np.cos(theta_s_2/180*np.pi)+np.cos((180-theta_t_2)/180*np.pi)


    if prove1 - a<0.0001:
        theta_t = theta_t_1
        theta_s = theta_s_1
    else:
        theta_t = theta_t_2
        theta_s = theta_s_2
    return theta_h, 180-theta_t, theta_s

def IK_right(x,y,z):

    theta_h = np.arctan2((-53.5+x),(21.5+z)) * 180 / np.pi - 180
    if theta_h<-15:
        theta_h+=360


    a = (14+y)/100
    b = (21.5+z)/-(np.cos(theta_h/180*np.pi)*100)

    value = 16*b*b-16*(a*a+b*b-4*a*a/(a*a+b*b))

    theta_sin_s_1 = (4*b+np.sqrt(value))/8
    theta_sin_t_1 = b - theta_sin_s_1
    theta_s_1 = np.arcsin(theta_sin_s_1)/np.pi*180
    theta_t_1 = np.arcsin(theta_sin_t_1)/np.pi*180


    theta_sin_s_2 = (4*b-np.sqrt(value))/8
    theta_sin_t_2 = b - theta_sin_s_2
    theta_s_2 = np.arcsin(theta_sin_s_2)/np.pi*180
    theta_t_2 = np.arcsin(theta_sin_t_2)/np.pi*180

    prove1 = np.cos(theta_s_1/180*np.pi)+np.cos((180-theta_t_1)/180*np.pi)
    prove2 = np.cos(theta_s_2/180*np.pi)+np.cos((180-theta_t_2)/180*np.pi)


    if prove1 - a<0.0001:
        theta_t = theta_t_1
        theta_s = theta_s_1
    else:
        theta_t = theta_t_2
        theta_s = theta_s_2
    return theta_h, 180-theta_t, theta_s


def norm(angles):
    hip = (angles[0] -  (-15)) /30
    thigh = (angles[1] - (95)) /65 
    shank = (angles[2] - (30)) /46

    # if angles[0]<-15 or angles[0]>15:
    #     print("the angle is out of the range")
    #     print("hip",angles[0])
    # elif angles[1]<95 or angles[1]>160:
    #     print("the angle is out of the range")
    #     print("thigh",angles[1])
    # elif angles[2]<30 or angles[2]>95:
    #     print("the angle is out of the range")
    #     print("shank",angles[2])
    return hip, thigh, shank



if __name__ == "__main__":



    # print(IK_left(-53.5,0,-218))#(0.0, 95.86427103573594, 75.98521720499733)
    # print(IK_right(53.5,0,-218))#(0.0, 95.86427103573594, 75.98521720499733)

    # print(IK_left(-94.28,0,-194.5)) #(13.263776966532362, 112.43909663617747, 58.553568358656804)
    # print(IK_right(94.28,0,-194.5)) #(-13.263776966532362, 112.43909663617747, 58.553568358656804)

    # print(IK_right(92.25,39.09,-185.89))


    # action_l = norm(IK_left(-94.28,0,-194.5))
    # action_r = norm(IK_right(94.28,0,-194.5))
    action_l = norm(IK_left(-34.28,0,-194.5))
    action_r = norm(IK_right(34.28,0,-194.5))
    print(action_l,action_r)
    # time1 = time.time()
    # print(IK_left(-53.5,-30,-189.61),IK_right(53.5,-30,-189.61)) #0.0004s
    # time2 = time.time()
    # print("time used:", time2-time1)

