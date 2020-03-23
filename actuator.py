import time
import RPi.GPIO as IO
from gpiozero import AngularServo

class actuatorController:

    def __init__(self):
        self._TRUEZERO = 5
        self.throttleScalingFactor = 0.25
        IO.setwarnings(False)
        IO.setmode(IO.BCM)
        IO.setup(12, IO.OUT)
        IO.setup(23, IO.OUT, initial=1)

        self._p = IO.PWM(12, 500)
        self._p.start(0)

        self._servo = AngularServo(13, min_angle=-90, max_angle=90)
        self._servo.angle = self._TRUEZERO

    def actuate(self,direction,throttle,angle,brake):
        if not brake:
             self._p.ChangeDutyCycle(throttle*self.throttleScalingFactor)
        else:
            self.throttle = 0

        if angle < 0:
            self._servo.angle = (angle/90 * 95) + self._TRUEZERO
        elif angle > 0:
            self._servo.angle = (angle/90 * 85) + self._TRUEZERO
        else:
            self._servo.angle =  self._TRUEZERO
        IO.output(23, direction)

    def stopAllMotors(self):
        self._p.stop()
        self.throttle = 0
        self.brake = True
     
    def releaseBrake(self):
        self.brake =False

    def setDirectionReverse(self):
        self.direction = 0

    #only call this on exit
    def exit(self):
        self._p.stop()
        self._servo.close()
        IO.cleanup()
        self.running  = False

        