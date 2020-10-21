
"""
author: Ethan Lipson (ethan.lipson@gmail.com)
"""


import serial
import time
import math

class ServoError(Exception):
    pass

class LX16A:
    controller = None
    
    ########### Initialization Functions ###########
    # Must be called before use!
    
    @staticmethod
    def initialize(port):
        LX16A.controller = serial.Serial(port=port, baudrate=115200)
    
    def __init__(self, ID):
        self.ID = ID
    
    ############### Utility Functions ###############
    
    @staticmethod
    def checksum(nums):
        s = ~sum(nums[2:])
        return s & 255

    @staticmethod
    def toBytes(n):
        return [n & 255, n // 256]
    
    @staticmethod
    def sendPacket(packet):
        packet.append(LX16A.checksum(packet))
        packet = bytes(packet)
        
        LX16A.controller.write(packet)
    
    @staticmethod
    def checkPacket(packet):
        if LX16A.checksum(packet[:-1]) != packet[-1]:
            raise ServoError("Invalid checksum")
            
    
    ################ Write Commands ################
    
    # Immediately after this command is sent,
    # rotate to the specified angle at uniform
    # speed, in the specified time
    
    # Possible angle values: [0, 1000], int
    # Possible time values (in milliseconds): [0, 30000], int
    
    def moveTimeWrite(self, angle, time=0):
        if angle < 0 or angle > 1000:
            raise ServoError("Angle out of range")
        if time < 0 or time > 30000:
            raise ServoError("Time out of range")
        
        packet = [0x55, 0x55, self.ID, 7, 1, *LX16A.toBytes(angle), *LX16A.toBytes(time)]
        LX16A.sendPacket(packet)
    
    # This command is similar to servo.moveTimeWrite,
    # except that the servo will not begin rotation
    # until it receives the servo.moveStart command
    
    # Possible angle values: [0, 1000], int
    # Possible time values (in milliseconds): [0, 30000], int
    
    def moveTimeWaitWrite(self, angle, time=0):
        if angle < 0 or angle > 1000:
            raise ServoError("Angle out of range")
        if time < 0 or time > 30000:
            raise ServoError("Time out of range")
        
        packet = [0x55, 0x55, self.ID, 7, 7, *LX16A.toBytes(angle), *LX16A.toBytes(time)]
        LX16A.sendPacket(packet)
    
    # To be used in conjunction with servo.moveTimeWaitWrite
    # Read the documentation for that command
    
    def moveStart(self):
        packet = [0x55, 0x55, self.ID, 3, 11]
        LX16A.sendPacket(packet)
    
    # Immediately halts all rotation,
    # regardless of the current state
    
    def moveStop(self):
        packet = [0x55, 0x55, self.ID, 3, 12]
        LX16A.sendPacket(packet)
    
    # Changes the servo's ID to the
    # parameter passed to this function
        
    # !!! BE CAREFUL WITH THIS COMMAND !!!
    # IT PERMANANTLY CHANGES THE ID OF THE SERVO
    # EVEN AFTER THE PROGRAM TERMINATES
    # AND AFTER THE SERVO POWERS DOWN
    # !!! YOU HAVE BEEN WARNED !!!
    
    # The ID of all servos is 1 by default
    # Possible ID values: [0, 253], int
    
    def IDWrite(self, ID):
        if ID < 0 or ID > 254:
            raise ServoError("ID out of range")
        packet = [0x55, 0x55, self.ID, 4, 13, ID]
        LX16A.sendPacket(packet)
        
        self.ID = ID
    
    # Adds a constant offset to the angle of rotation
    
    # For example, if the offset is -125 (-30 degrees),
    # and the servo is commanded to rotate to position
    # 500 (120 degrees), it will rotate to position 375
    # (90 degrees)
    
    # The offset resets back to 0 when the servo powers off
    # However, it can be permanently set using servo.angleOffsetWrite
    
    # The offset is 0 by default
    # Possible angle values: [-125, 125], int
    
    def angleOffsetAdjust(self, offset):
        if offset < -125 or offset > 125:
            raise ServoError("Offset out of range")
        
        if offset < 0:
            offset += 256
        
        packet = [0x55, 0x55, self.ID, 4, 17, offset]
        LX16A.sendPacket(packet)
    
    # Permanently applies the offset angle set by
    # servoAngleOffsetAdjust. After the servo powers
    # down, the offset will default to the set angle
    
    def angleOffsetWrite(self):
        packet = [0x55, 0x55, self.ID, 3, 18]
        LX16A.sendPacket(packet)
    
    # Permanently sets a restriction on the rotation
    # angle. If the current angle is outside of the bounds,
    # nothing will change. But once the angle enters the legal range,
    # it will not be allowed to exceed the limits until they are extended
    
    # After restrictions are applied, the angles will not scale
    # For example, if the bounds are set to [500, 1000], the angle 0
    # does not mean a rotation of halfway
    
    # The lower bound must always be less than the upper bound
    # The default angle limits are 0 and 1000
    # Possible lower values: [0, 1000], int
    # Possible upper values: [0, 1000], int
    
    def angleLimitWrite(self, lower, upper):
        if lower < 0 or lower > 1000:
            raise ServoError("Lower bound out of range")
        if upper < 0 or upper > 1000:
            raise ServoError("Upper bound out of range")
        if lower >= upper:
            raise ServoError("Lower bound must be less than upper bound")
        
        packet = [0x55, 0x55, self.ID, 7, 20, *LX16A.toBytes(lower), *LX16A.toBytes(upper)]
        LX16A.sendPacket(packet)
    
    # Sets the lower and upper bounds on the input voltage
    
    # If the input voltage exceeds these bounds, the LED
    # on the servo will flash and the servo will not rotate
    
    # Possible lower values (in millivolts): [4500, 12000], int
    # Possible higher values (in millivolts): [4500, 12000], int
    
    def vInLimitWrite(self, lower, upper):
        if lower < 4500 or lower > 12000:
            raise ServoError("Lower bound out of range")
        if upper < 4500 or upper > 12000:
            raise ServoError("Upper bound out of range")
        if lower >= upper:
            raise ServoError("Lower bound must be less than upper bound")
        
        packet = [0x55, 0x55, self.ID, 7, 22, *LX16A.toBytes(lower), *LX16A.toBytes(upper)]
        LX16A.sendPacket(packet)

    # Sets the maximum internal temperature
    
    # If the servo temperature exceeds the limit, the LED
    # on the servo will flash and the servo will not rotate
    
    # Default maximum temperature is 85 degrees
    # Possible temperature values (in degrees celcius): [50, 100], int
    
    def tempMaxLimitWrite(self, temp):
        if temp < 50 or temp > 100:
            raise ServoError("Temperature limit out of range")
        
        packet = [0x55, 0x55, self.ID, 4, 24, temp]
        LX16A.sendPacket(packet)
    
    # The LX-16A has two modes:
    # Servo mode (with precise angle control)
    # Motor mode (with continuous rotation)
    
    # This command sets the servo to servo mode
    
    def servoMode(self):
        packet = [0x55, 0x55, self.ID, 7, 29, 0, 0, 0, 0]
        LX16A.sendPacket(packet)
    
    # This command sets the servo to motor mode
    
    # The speed parameter controls how fast
    # the servo spins
    
    # -1000 is full speed backwards, and
    # 1000 is full speed forwards
    # Possible speed values: [-1000, 1000], int
    
    def motorMode(self, speed):
        if speed < -1000 or speed > 1000:
            raise ServoError("Speed out of range")
        
        if speed < 0:
            speed += 65536
        
        packet = [0x55, 0x55, self.ID, 7, 29, 1, 0, *LX16A.toBytes(speed)]
        LX16A.sendPacket(packet)
    
    # Controls the power state of the servo
    
    # In the power down state, the servo consumes
    # less power, but will also not respond to commands
    # It will respond once powered on
    
    # Possible power values:
    # 0 for power down, 1 for power on
    
    def loadOrUnloadWrite(self, power):
        if power != 0 and power != 1:
            raise ServoError("Power must be 0 or 1")
        
        packet = [0x55, 0x55, self.ID, 4, 31, power]
        LX16A.sendPacket(packet)
    
    # Controls the error LED on the back of the servo
    
    # Possible power values:
    # 1 means always off (will not report errors)
    # 0 means always on (able to report errors)
    
    def LEDCtrlWrite(self, power):
        if power != 0 and power != 1:
            raise ServoError("Power must be 0 or 1")
        
        packet = [0x55, 0x55, self.ID, 4, 33, power]
        LX16A.sendPacket(packet)
    
    # Controls what conditions will cause
    # the error LED to flash
    
    # If temp is true, the LED will flash
    # when the temperature limit is exceeded
    
    # If volt is true, the LED will flash
    # when the input voltage is outside the bounds
    
    # If lock is true, the LED will flash
    # when the internal rotor is locked
    
    def LEDErrorWrite(self, temp, volt, lock):
        val = 0
        
        val += 1 if temp else 0
        val += 2 if volt else 0
        val += 4 if lock else 0
        
        packet = [0x55, 0x55, self.ID, 4, 35, val]
        LX16A.sendPacket(packet)
    
    ################# Read Commands #################
    
    # Returns the parameters of the most recent
    # servo.moveTimeWrite command
    
    # Parameter order:
    # [Angle, time (in milliseconds)]
    
    def moveTimeRead(self):
        packet = [0x55, 0x55, self.ID, 3, 2]
        LX16A.sendPacket(packet)
        
        returned = []
        
        for i in range(10):
            returned.append(LX16A.controller.read())
        
        returned = [int.from_bytes(b, byteorder="little") for b in returned]
        LX16A.checkPacket(returned)
        
        data = [returned[6] * 256 + returned[5], returned[8] * 256 + returned[7]]
        
        return data
    
    # Returns the parameters of the most recent
    # servo.moveTimeWaitWrite command
    
    # Parameter order:
    # [Angle, time (in milliseconds)]
    
    ### THIS FUNCTION IS DYSFUNCTIONAL ###
    ###### DO NOT USE IT AS OF NOW ######
    
    def moveTimeWaitRead(self):
        print("This function (servo.moveTimeWaitRead) does not work right now")
        print("It will be fixed in a future update")
        return
        
        packet = [0x55, 0x55, self.ID, 3, 8]
        LX16A.sendPacket(packet)
        
        returned = []
        
        for i in range(10):
            returned.append(LX16A.controller.read())
        
        returned = [int.from_bytes(b, byteorder="little") for b in returned]
        LX16A.checkPacket(returned)
        
        data = [returned[6] * 256 + returned[5], returned[8] * 256 + returned[7]]
        
        return data
    
    # Returns the ID of the servo
    
    def IDRead(self):
        packet = [0x55, 0x55, self.ID, 3, 14]
        LX16A.sendPacket(packet)
        
        returned = []

        for i in range(7):
            returned.append(LX16A.controller.read())
        
        returned = [int.from_bytes(b, byteorder="little") for b in returned]
        LX16A.checkPacket(returned)
        
        data = returned[5]
        
        return data
    
    # Returns the angle offset of the servo
    # Refer to servo.angleOffsetAdjust for more information
    
    def angleOffsetRead(self):
        packet = [0x55, 0x55, self.ID, 3, 19]
        LX16A.sendPacket(packet)
        
        returned = []
        
        for i in range(7):
            returned.append(LX16A.controller.read())
        
        returned = [int.from_bytes(b, byteorder="little") for b in returned]
        LX16A.checkPacket(returned)
        
        return returned[5] - 256 if returned[5] > 127 else returned[5]
    
    # Returns the upper and lower angle limits of the servo
    # Refer to servo.angleLimitWrite for more information
    
    def angleLimitRead(self):
        packet = [0x55, 0x55, self.ID, 3, 21]
        LX16A.sendPacket(packet)
        
        returned = []
        
        for i in range(10):
            returned.append(LX16A.controller.read())
        
        returned = [int.from_bytes(b, byteorder="little") for b in returned]
        LX16A.checkPacket(returned)
        
        data = [returned[6] * 256 + returned[5], returned[8] * 256 + returned[7]]
        
        return data
    
    # Returns the upper and lower input voltage limits
    # of the servo
    # Refer to servo.vInLimitWrite for more information
    
    def vInLimitRead(self):
        packet = [0x55, 0x55, self.ID, 3, 23]
        LX16A.sendPacket(packet)
        
        returned = []
        
        for i in range(10):
            returned.append(LX16A.controller.read())
        
        returned = [int.from_bytes(b, byteorder="little") for b in returned]
        LX16A.checkPacket(returned)
        
        data = [returned[6] * 256 + returned[5], returned[8] * 256 + returned[7]]
        
        return data
    
    # Returns the internal temperature limit of the servo
    # Refer ot servo.tempMaxLimitWrite for more information
    
    def tempMaxLimitRead(self):
        packet = [0x55, 0x55, self.ID, 3, 25]
        LX16A.sendPacket(packet)
        
        returned = []
        
        for i in range(7):
            returned.append(LX16A.controller.read())
        
        returned = [int.from_bytes(b, byteorder="little") for b in returned]
        LX16A.checkPacket(returned)
        
        return returned[5]
    
    # Returns the internal temperature of the servo, in degrees celcius
    
    def tempRead(self):
        packet = [0x55, 0x55, self.ID, 3, 26]
        LX16A.sendPacket(packet)
        
        returned = []
        
        for i in range(7):
            returned.append(LX16A.controller.read())
        
        returned = [int.from_bytes(b, byteorder="little") for b in returned]
        LX16A.checkPacket(returned)
        
        return returned[5]
    
    # Returns the input voltage of the servo, in millivolts
    
    def vInRead(self):
        packet = [0x55, 0x55, self.ID, 3, 27]
        LX16A.sendPacket(packet)
        
        returned = []
        
        for i in range(8):
            returned.append(LX16A.controller.read())
        
        returned = [int.from_bytes(b, byteorder="little") for b in returned]
        LX16A.checkPacket(returned)
        
        return returned[6] * 256 + returned[5]
    
    # Returns the position of the servo
    # Note that the position is relative to the angle offset
    
    # So if you set the angle offset to -125
    # and then set the position to 0, it will still read
    # as being in position 0
    
    def posRead(self):
        packet = [0x55, 0x55, self.ID, 3, 28]
        LX16A.sendPacket(packet)
        
        returned = []
        
        for i in range(8):
            returned.append(LX16A.controller.read())
        
        returned = [int.from_bytes(b, byteorder="little") for b in returned]
        LX16A.checkPacket(returned)
        
        return returned[6] * 256 + returned[5]
    
    # Returns the mode of the servo, and if it is in motor mode,
    # the motor speed is also returned
    # Refer to servo.servoMode and servo.motorMode for more information
    
    def servoOrMotorModeRead(self):
        packet = [0x55, 0x55, self.ID, 3, 30]
        LX16A.sendPacket(packet)
        
        returned = []
        
        for i in range(10):
            returned.append(LX16A.controller.read())
        
        LX16A.checkPacket([int.from_bytes(b, byteorder="little") for b in returned])
        
        if int.from_bytes(returned[5], byteorder="little") == 0:
            return 0
        else:
            speed = int.from_bytes(returned[7] + returned[8], byteorder="little")
            
            if speed > 32767:
                speed -= 65536
            
            return [1, speed]
    
    # Returns the power state of the servo
    # Refer to servo.loadOrUnloadWrite for more information
    
    # Causing problems currently
    
    def loadOrUnloadRead(self):
        packet = [0x55, 0x55, self.ID, 3, 32]
        LX16A.sendPacket(packet)
        
        returned = []
        
        for i in range(7):
            returned.append(LX16A.controller.read())
        
        returned = [int.from_bytes(b, byteorder="little") for b in returned]
        LX16A.checkPacket(returned)
        
        return returned[5]
    
    # Returns the LED on/off state
    # Refer to LEDCtrlWrite for more information
    
    def LEDCtrlRead(self):
        packet = [0x55, 0x55, self.ID, 3, 34]
        LX16A.sendPacket(packet)
        
        returned = []
        
        for i in range(7):
            returned.append(LX16A.controller.read())
        
        returned = [int.from_bytes(b, byteorder="little") for b in returned]
        LX16A.checkPacket(returned)
        
        return returned[5]
    
    # Returns what faults will cause the LED to flash
    
    # If the first value is 1, then the LED will flash when the internal
    # temperature is over the limit
    
    # If the second value is 1, then the LED will flash when the input
    # voltage is out of bounds
    
    # If the third value is 1, then the LED will flash when the rotor
    # is locked
    
    # Refer to LEDErrorWrite for more information
    
    def LEDErrorRead(self):
        packet = [0x55, 0x55, self.ID, 3, 36]
        LX16A.sendPacket(packet)
        
        returned = []
        
        for i in range(7):
            returned.append(LX16A.controller.read())
        
        returned = [int.from_bytes(b, byteorder="little") for b in returned]
        LX16A.checkPacket(returned)
        
        temp = int(bool(returned[5] & 1))
        volt = int(bool(returned[5] & 2))
        lock = int(bool(returned[5] & 4))
        
        return [temp, volt, lock]







