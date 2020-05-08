from actuator import actuatorController
from joycon import joycon
from DataGathering import recorder
from CommandParser import commandLineInterface
from autodriver import autodriver_actuator
from autodriver import autodriver_controller
from Allinonedriver import  DriveAgent as DA

import threading

#Button Codes
#### ANALOG STICKS ####
# ABS_X --> LeftStick x Axis
# ABS_Y --> LeftStick y Axis
# ABS_Z --> RightStick x Axis
# ABS_RZ --> RightStick y Axis

#### ABXY Buttons ####
# BTN_EAST --> A
# BTN_SOUTH --> X
# BTN_NORTH --> Y
# BTN_C --> B

#### DPAD ####
# ABS_HAT0Y --> -1 : up
# ABS_HAT0Y --> 1 : down
# ABS_HAT0X --> -1 : Left
# ABS_HAT0X --> 1 : Right

#### Bumper ####
# BTN_Z --> Right Bumper
# BTN_WEST --> Left Bumper
# BTN_TR --> Right Trigger
# BTN_TL --> Left Trigger


# ButtonHandlers ={
#     #### ANALOG STICKS ####
#     "ABS_X": HandleLeftStick_X_Axis,
#     "ABS_Y": HandleLeftStick_Y_Axis,
#     "ABS_Z": HandleRightStick_X_Axis,
#     "ABS_RZ": HandleRightStick_Y_Axis,

#     #### ABXY Buttons ####
#     "BTN_EAST": HandleBtn_A,
#     "BTN_SOUTH": HandleBtn_X,
#     "BTN_NORTH": HandleBtn_Y,
#     "BTN_C": HandleBtn_B,

#     #### DPAD ####
#     "ABS_HAT0Y": HandleDpad_Y,
#     "ABS_HAT0X": HandleDpad_X,

#     #### Bumper ####
#     "BTN_Z":HandleRightBumper,
#     "BTN_WEST":HandleLeftBumper,
#     "BTN_TR":HandleRightTrigger,
#     "BTN_TL":HandleLeftTrigger
# }
class top:
    def __init__(self):
        self.actuator = actuatorController()
        self.joycon = joycon()
        #self.recorder = recorder()
        ##self.CLI = commandLineInterface()
        self.autoActuator = autodriver_actuator()
        ##self.autoController = autodriver_controller()
        self.autopilot =False


        self.actuator.setTop(self)
        self.joycon.setTop(self)
        #self.recorder.setTop(self)
        ##self.CLI.setTop(self)
        ##self.autoController.setTop(self)
        self.autoActuator.setTop(self)

        self.actuator.setController(self.joycon)
        self.controllerThread = threading.Thread(target=self.joycon.run)
        ##self.recorderThread = threading.Thread(target=self.recorder.run)
        ##self.autoControllerThread = threading.Thread(target=self.autoController.run)

    def run(self):
        try:
            #self.controllerThread.start()
            #self.recorderThread.start()
            #self.autoControllerThread.start()
            self.DA_obj = DA(self)
            self.DA_obj.run()
            #self.recorderThread.join()
            #self.autoControllerThread.join()
            print("exiting")
        except KeyboardInterrupt:
            print("Caught Keyboard Interrupt!")
            #self.joycon.exit()
            #self.recorder.exit()
            #self.autoController.exit()
            #self.controllerThread.join()
            #self.recorderThread.join()
           # self.autoControllerThread.join()
            print("Exit.")
            
    def exit(self):
        self.joycon.exit()
        #self.recorder.exit()
        #self.autoController.exit()

def main():
    t = top()
    t.run()



if __name__ == "__main__":
    main()