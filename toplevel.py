from actuator import actuatorController
from joycon import joycon
from DataGathering import recorder
from CommandParser import commandLineInterface
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


    
def main():
    try:
        motor = actuatorController()
        print("Created Actuator Objects")
        controller = joycon(motor)
        print("Created Controller Objects")
        recorderInstance = recorder(controller)
        controller.setRecorder(recorderInstance)
        print("Created recorder Objects")

        mods = {
            "recorder": recorderInstance,
            "controller":controller,
            "actuator":motor
        }
        CLI = commandLineInterface(mods)
        print("Created CLI Instance")
        controllerThread = threading.Thread(target=controller.run)
        recorderThread = threading.Thread(target=recorderInstance.run)

        controllerThread.start()
        recorderThread.start()

        CLI.run()

        controllerThread.join()
        recorderThread.join()
        print("exiting")

    except KeyboardInterrupt:
        print("Caught Keyboard Interrupt!")
        controller.exit()
        recorderInstance.exit()
        controllerThread.join()
        recorderThread.join()



if __name__ == "__main__":
    main()