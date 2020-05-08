import threading
import time
from math import floor
class autodriver_controller:
    def __init__(self):
        self.isExit = False
        self.disabled = True
        self.commandsPerSecond = 5

        def generateTestCommandLoop():
            def generateCommand(secs, command):
                return [command]*(floor(secs*self.commandsPerSecond))
            cmd = generateCommand(1.2,"straight") +  generateCommand(0.2,"drift_right")
            return cmd
        
        self.testCommands = generateTestCommandLoop()

            


    def setTop(self,top):
        self.top = top
        self.autodriver_actuator = top.autoActuator

    def run_test_loop(self):
        for i in range(len(self.testCommands)):
            if self.isExit or self.disabled:
                break
            self.autodriver_actuator.processCommand(self.testCommands[i])
            time.sleep(1/self.commandsPerSecond)

    
    def disable(self):
        self.autodriver_actuator.stop()
        self.disabled =True
        self.top.actuator.setController(self.top.joycon)
        print("Autodrive Disabled")
    def enable(self):
        self.top.actuator.setController(self.autodriver_actuator)
        self.disabled =False
        print("Autodrive Enabled")

    def run(self):
        print('Autodriver Thread started')
        while not self.isExit:
            while not self.disabled:
                self.run_test_loop()
        print('Autodriver Thread Closed!')
    
    def exit(self):
        print('Closing Autodriver Thread')
        if not self.disabled:
            self.disable()
        self.isExit =True

class autodriver_actuator:
    def __init__(self):
        self.top = None
        self.actuator = None

        self.drifting =False

        self.correct_left_parameters ={
            #"duration" : 0.5, #in seconds
            "angle" :  -50 , # in degrees from center, left is negative, right is positive
            "throttle": 5 #value from [0,100]
        }
        self.correct_right_parameters ={
            #"duration" : 0.5, #in seconds
            "angle" :  50 , # in degrees from center, left is negative, right is positive
            "throttle": 5 #value from [0,100]
        }
        self.hard_right_parameters ={
            "duration" : 0.5, #in seconds
            "angle" :  90 , # in degrees from center, left is negative, right is positive
            "throttle": 60 #value from [0,100]
        }
        self.straight_parameters ={
            #"duration" : 0.5, #in seconds
            "angle" :  0 , # in degrees from center, left is negative, right is positive
            "throttle": 5 #value from [0,100]
        }

        self.commands ={
            "correct_left": self.correct_left,
            "correct_right": self.correct_right,
            "drift_right":self.drift_right,
            "cancel_drift":self.cancel_drift,
            "stop":self.stop,
            "straight": self.straight
        }
    def setTop(self,top):
        self.top = top
        self.actuator = top.actuator

    def correct_left(self):
        self.actuator.setController(self)
        self.actuator.actuate(1,self.correct_left_parameters["throttle"],self.correct_left_parameters["angle"],0,self)
        self.actuator.setController(self.top.joycon)
    def correct_right(self):
        self.actuator.setController(self)
        self.actuator.actuate(1,self.correct_right_parameters["throttle"],self.correct_right_parameters["angle"],0,self)
        self.actuator.setController(self.top.joycon)
    def straight(self):
        self.actuator.setController(self)
        self.actuator.actuate(1,self.straight_parameters["throttle"],self.straight_parameters["angle"],0,self)
        self.actuator.setController(self.top.joycon)
    def hard_right(self):
        self.actuator.actuate(1,self.hard_right_parameters["throttle"],self.hard_right_parameters["angle"],0,self)
    def cancel_drift(self):
        if self.drifting:
            self.drifting = False
            self.straight()
    def stop(self):
        self.cancel_drift()
        self.actuator.actuate(1,0,0,0,self)
    def processCommand(self, command):
        c = self.commands.get(command)
        if (not (c is None)) and self.drifting == False :
            #print(command)
            c()
        elif command =="cancel_drift" and self.drifting == True:
            c()
        else:
            #empty branch should not reach
            pass
    def drift_right(self):
        self.drifting =True
        self.hard_right()
        timer = threading.Timer(self.hard_right_parameters["duration"],self.cancel_drift)
        timer.start()
        #not sure if i need to destroy this object manually.
        #The Garbage collector should do it for me automatically, but if not then this is a memory leak
        #else use a time loop
    def drift_right_manual(self):
        print("start_drift")
        self.actuator.setController(self)
        self.drifting =True

        self.actuator.actuate(1,20,90,0,self)
        time.sleep(0.2)
        self.hard_right()
        # timer = threading.Timer(self.hard_right_parameters["duration"],self.cancel_drift)
        # timer.start()
        # while(self.drifting):
        #     pass
        time.sleep(self.hard_right_parameters["duration"])
        self.actuator.actuate(1,0,0,0,self)
        time.sleep(0.2)
        self.actuator.actuate(1,5,90,0,self)
        time.sleep(1)
        self.actuator.actuate(1,5,0,0,self)
        time.sleep(1)
        self.actuator.actuate(1,0,0,0,self)
        time.sleep(0.1)
        self.actuator.actuate(1,5,-50,0,self)
        time.sleep(0.5)
        self.actuator.actuate(1,5,0,0,self)
        self.actuator.setController(self.top.joycon)
        print("end_drift")
        #not sure if i need to destroy this object manually.
        #The Garbage collector should do it for me automatically, but if not then this is a memory leak
        #else use a time loop

    def drift_right_manual2(self):
        print("start_drift2a")
        self.actuator.setController(self)
        self.drifting =True

        self.actuator.actuate(1,20,90,0,self)
        time.sleep(0.2)
        self.hard_right()
        # timer = threading.Timer(self.hard_right_parameters["duration"],self.cancel_drift)
        # timer.start()
        # while(self.drifting):
        #     pass
        time.sleep(self.hard_right_parameters["duration"])
        self.actuator.actuate(1,0,0,0,self)
        time.sleep(0.2)
        # self.actuator.actuate(1,5,50,0,self)
        # time.sleep(1)
        self.actuator.actuate(1,5,0,0,self)
        time.sleep(1.5)
        self.actuator.actuate(1,5,0,0,self)
        self.actuator.setController(self.top.joycon)
        print("end_drift2")