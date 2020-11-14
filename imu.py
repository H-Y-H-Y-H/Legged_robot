from adafruit_lsm6ds.lsm6dsox import LSM6DSOX as LSM6DS
from adafruit_lis3mdl import LIS3MDL
from scipy.spatial.transform import Rotation as R
import board
import numpy as np
import time
import math

accel_gyro = LSM6DS(board.I2C())
magnetic = LIS3MDL(board.I2C())

GRAVITY = 9.802 # The gravity acceleration in New York City

# Calibration outcomes

GYRO_X_OFFSET =  -0.0065253241282558294
GYRO_Y_OFFSET =  0.01928664896811285
GYRO_Z_OFFSET =  -0.008492265774529259
      
ACCEL_X_OFFSET = -0.11185932038794569 
ACCEL_Y_OFFSET = 0.6418540129821427
ACCEL_Z_OFFSET =  9.851294249168042



magn_ellipsoid_center = np.array([-6.82542614, -19.00300855, 68.77762737])
magn_ellipsoid_transform = np.array([[ 0.75054184, -0.02235841, -0.01846452],
 [-0.02235841 , 0.83891538 ,-0.05385916],
 [-0.01846452 ,-0.05385916  ,0.98150185]])

time_former = 0

q = [1, 0, 0, 0]

def read_sensors():
    acc = np.array(accel_gyro.acceleration)
    mag = np.array(magnetic.magnetic)
    gyr = np.array(accel_gyro.gyro)
    return acc, gyr, mag

def compensate_sensor_errors(acc, gyr, mag):
    # Compensate accelerometer error
    acc[0] -= ACCEL_X_OFFSET
    acc[1] -= ACCEL_Y_OFFSET
    acc[2] -= ACCEL_Z_OFFSET - GRAVITY

    # Compensate magnetometer error
    mag_tmp = mag - magn_ellipsoid_center
    mag = magn_ellipsoid_transform.dot(mag_tmp)

    # Compensate gyroscope error
    gyr[0] -= GYRO_X_OFFSET
    gyr[1] -= GYRO_Y_OFFSET
    gyr[2] -= GYRO_Z_OFFSET
    
    return acc, gyr, mag

# Madgwick filter
def MadgwickQuaternionUpdate(acc, gyr, mag, deltat):
    # Beta is regression step. When it increases, estimation algorithm responds faster but it will be more oscillation in outcomes.
    beta = 8
    q1, q2, q3, q4 = q[0], q[1], q[2], q[3]
    ax, ay, az = acc[0], acc[1], acc[2]
    gx, gy, gz = gyr[0], gyr[1], gyr[2]
    mx, my, mz = mag[0], mag[1], mag[2]
    # Auxiliary variables to avoid repeated arithmetic
    _2q1 = 2 * q1
    _2q2 = 2 * q2
    _2q3 = 2 * q3
    _2q4 = 2 * q4
    _2q1q3 = 2 * q1 * q3
    _2q3q4 = 2 * q3 * q4
    q1q1 = q1 * q1
    q1q2 = q1 * q2
    q1q3 = q1 * q3
    q1q4 = q1 * q4
    q2q2 = q2 * q2
    q2q3 = q2 * q3
    q2q4 = q2 * q4
    q3q3 = q3 * q3
    q3q4 = q3 * q4
    q4q4 = q4 * q4

    # Normalise accelerometer measurement
    norm = 1 / math.sqrt(ax * ax + ay * ay + az * az)
    ax *= norm
    ay *= norm
    az *= norm

    # Normalise magnetometer measurement
    norm = 1 / math.sqrt(mx * mx + my * my + mz * mz)
    mx *= norm
    my *= norm
    mz *= norm

    # Reference direction of Earth's magnetic field
    _2q1mx = 2 * q1 * mx
    _2q1my = 2 * q1 * my
    _2q1mz = 2 * q1 * mz
    _2q2mx = 2 * q2 * mx
    hx = mx * q1q1 - _2q1my * q4 + _2q1mz * q3 + mx * q2q2 + _2q2 * my * q3 + _2q2 * mz * q4 - mx * q3q3 - mx * q4q4
    hy = _2q1mx * q4 + my * q1q1 - _2q1mz * q2 + _2q2mx * q3 - my * q2q2 + my * q3q3 + _2q3 * mz * q4 - my * q4q4
    _2bx = math.sqrt(hx * hx + hy * hy)
    _2bz = -_2q1mx * q3 + _2q1my * q2 + mz * q1q1 + _2q2mx * q4 - mz * q2q2 + _2q3 * my * q4 - mz * q3q3 + mz * q4q4
    _4bx = 2 * _2bx
    _4bz = 2 * _2bz

    # Gradient decent algorithm corrective step
    s1 = -_2q3 * (2 * q2q4 - _2q1q3 - ax) + _2q2 * (2 * q1q2 + _2q3q4 - ay) - _2bz * q3 * (_2bx * (0.5 - q3q3 - q4q4) + _2bz * (q2q4 - q1q3) - mx) + (-_2bx * q4 + _2bz * q2) * (_2bx * (q2q3 - q1q4) + _2bz * (q1q2 + q3q4) - my) + _2bx * q3 * (_2bx * (q1q3 + q2q4) + _2bz * (0.5 - q2q2 - q3q3) - mz)
    s2 = _2q4 * (2 * q2q4 - _2q1q3 - ax) + _2q1 * (2 * q1q2 + _2q3q4 - ay) - 4 * q2 * (1 - 2 * q2q2 - 2 * q3q3 - az) + _2bz * q4 * (_2bx * (0.5 - q3q3 - q4q4) + _2bz * (q2q4 - q1q3) - mx) + (_2bx * q3 + _2bz * q1) * (_2bx * (q2q3 - q1q4) + _2bz * (q1q2 + q3q4) - my) + (_2bx * q4 - _4bz * q2) * (_2bx * (q1q3 + q2q4) + _2bz * (0.5 - q2q2 - q3q3) - mz)
    s3 = -_2q1 * (2 * q2q4 - _2q1q3 - ax) + _2q4 * (2 * q1q2 + _2q3q4 - ay) - 4 * q3 * (1 - 2 * q2q2 - 2 * q3q3 - az) + (-_4bx * q3 - _2bz * q1) * (_2bx * (0.5 - q3q3 - q4q4) + _2bz * (q2q4 - q1q3) - mx) + (_2bx * q2 + _2bz * q4) * (_2bx * (q2q3 - q1q4) + _2bz * (q1q2 + q3q4) - my) + (_2bx * q1 - _4bz * q3) * (_2bx * (q1q3 + q2q4) + _2bz * (0.5 - q2q2 - q3q3) - mz)
    s4 = _2q2 * (2 * q2q4 - _2q1q3 - ax) + _2q3 * (2 * q1q2 + _2q3q4 - ay) + (-_4bx * q4 + _2bz * q2) * (_2bx * (0.5 - q3q3 - q4q4) + _2bz * (q2q4 - q1q3) - mx) + (-_2bx * q1 + _2bz * q3) * (_2bx * (q2q3 - q1q4) + _2bz * (q1q2 + q3q4) - my) + _2bx * q2 * (_2bx * (q1q3 + q2q4) + _2bz * (0.5 - q2q2 - q3q3) - mz)
    norm = math.sqrt(s1 * s1 + s2 * s2 + s3 * s3 + s4 * s4)    # normalise step magnitude
    norm = 1 / norm
    s1 *= norm
    s2 *= norm
    s3 *= norm
    s4 *= norm

    # Compute rate of change of quaternion
    qDot1 = 0.5 * (-q2 * gx - q3 * gy - q4 * gz) - beta * s1
    qDot2 = 0.5 * (q1 * gx + q3 * gz - q4 * gy) - beta * s2
    qDot3 = 0.5 * (q1 * gy - q2 * gz + q4 * gx) - beta * s3
    qDot4 = 0.5 * (q1 * gz + q2 * gy - q3 * gx) - beta * s4

    # Integrate to yield quaternion
    q1 += qDot1 * deltat
    q2 += qDot2 * deltat
    q3 += qDot3 * deltat
    q4 += qDot4 * deltat
    norm = math.sqrt(q1 * q1 + q2 * q2 + q3 * q3 + q4 * q4)    # normalise quaternion
    norm = 1 / norm;
    q[0] = q1 * norm
    q[1] = q2 * norm
    q[2] = q3 * norm
    q[3] = q4 * norm

def ToEulerAngles(qua):
    sinr_cosp = 2 * (qua[0] * qua[1] + qua[2] * qua[3])
    cosr_cosp = 1 - 2 * (qua[1] * qua[1] + qua[2] * qua[2])
    roll_e = math.atan2(sinr_cosp, cosr_cosp)

    sinp = 2 * (qua[0] * qua[2] - qua[3] * qua[1])
    if (abs(sinp) >= 1):
        pitch_e = math.copysign(M_PI / 2, sinp)
    else:
        pitch_e = math.asin(sinp)

    siny_cosp = 2 * (qua[0] * qua[3] + qua[1] * qua[2])
    cosy_cosp = 1 - 2 * (qua[2] * qua[2] + qua[3] * qua[3])
    yaw_e = math.atan2(siny_cosp, cosy_cosp)

    return np.array([roll_e, pitch_e, yaw_e])


def output(time_former):
    acc ,gyr, mag = read_sensors()
    acc ,gyr, mag = compensate_sensor_errors(acc ,gyr, mag)
    for _ in range(25):
        time_now = time.time()
        deltat = time_now - time_former
        time_former = time_now
        MadgwickQuaternionUpdate(acc, gyr, mag, deltat)
    
    euler = ToEulerAngles(q)
    euler *= 180 / math.pi
    euler[2] -= 82; # 60 this used for compensating the angle between magenatic north and geographic north, change this number at will
    if (euler[2] < -180):
        euler[2] += 360
    return euler

if __name__ == '__main__':
    time_former = time.time()
    a = 0
    for i in range(10000):
        data = output(time_former)
        
        print(data)
        time_former = time.time()



