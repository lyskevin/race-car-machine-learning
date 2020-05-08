import time
import RPi.GPIO as IO
from gpiozero import AngularServo
from joycon import joycon

class actuatorController:

    def __init__(self):
        self.top = None

        ###Scaling Constants###
        self._TRUEZERO = 5
        self.throttleScalingFactor = 1

        ###Input states###
        self.direction = 1 #1 = Forward | 0 = Backward
        self.throttle = 0 
        self.turnAngle= 0 
        self.brake = False

        ###Input Source###
        self.controller = None


        IO.setwarnings(False)
        IO.setmode(IO.BCM)
        IO.setup(12, IO.OUT)
        IO.setup(23, IO.OUT, initial=1)

        self._p = IO.PWM(12, 500)
        self._p.start(0)

        self._servo = AngularServo(13, min_angle=-90, max_angle=90)
        self._servo.angle = self._TRUEZERO

    def setTop(self,top):
        self.top = top
    def getController(self):
        return self.controller
    def setController(self,controller):
        self.controller = controller


    def actuate(self,direction,throttle,angle,brake,controller):
        if not (self.controller is controller):
            #print(self.direction,self.throttle, self.turnAngle, self.brake)
            return None
        elif (type(self.controller) ==  joycon):
            throttle = throttle * 0.05
        self.direction = direction
        self.throttle = throttle
        self.turnAngle = angle
        self.brake = brake
        

        if not brake:
             self._p.ChangeDutyCycle(throttle*self.throttleScalingFactor)
        else:
            self.throttle = 0
            self._p.ChangeDutyCycle(self.throttle*self.throttleScalingFactor)

        if angle < 0:
            self._servo.angle = (angle/90 * 95) + self._TRUEZERO
        elif angle > 0:
            self._servo.angle = (angle/90 * 85) + self._TRUEZERO
        else:
            self._servo.angle =  self._TRUEZERO
        IO.output(23, direction)
    def getControlState(self):
        return (self.direction,self.throttle, self.turnAngle, self.brake)

    #only call this on exit
    def exit(self):
        self._p.stop()
        self._servo.close()
        IO.cleanup()
        self.running  = False

        