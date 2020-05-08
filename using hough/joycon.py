from inputs import get_gamepad

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


class joycon:
    _CONTROLLER_ANALOG_MAX_VAL = 255
    _CONTROLLER_ANALOG_MIDDLE_VAL = 127
    _CONTROLLER_ANALOG_DEADZONE_OFFSET = 5

    def __init__(self):
        self.isExit = False
        self.disabled = True

        self.top = None
        self.actuator = None
        

        self._ButtonHandlersNormal ={
            #### ANALOG STICKS ####
            "ABS_X": self.processTurn,
            "ABS_Y": self.nullControl,
            "ABS_Z": self.nullControl,
            "ABS_RZ": self.processThrottle,

            #### ABXY Buttons ####
            "BTN_EAST": self.steadyThrottle,
            "BTN_SOUTH": self.processToggleAuto,
            "BTN_NORTH": self.nullControl,
            "BTN_C": self.nullControl,

            #### DPAD ####
            "ABS_HAT0Y": self.nullControl,
            "ABS_HAT0X": self.nullControl,

            #### Bumper ####
            "BTN_Z": self.processDriftRight,
            "BTN_WEST": self.nullControl,
            "BTN_TR": self.nullControl,
            "BTN_TL": self.nullControl,

            #### Start ####
            "BTN_TR2": self.processRecord,
            "BTN_TL2": self.nullControl,
        }
        self.handlers = self._ButtonHandlersNormal

    def setTop(self,top):
        self.top = top
        self.actuator = top.actuator

    def processEvent(self,e):
        if e.ev_type == 'Key' or e.ev_type == 'Absolute':
            hdlr = self.handlers.get(e.code)
            if (not hdlr is None) and (not self.disabled) :
                hdlr(e)
        
    def nullControl(self,e):
        return None

    def processThrottle(self,e):
        #print('Set Throttle: ', e.state)
        if e.state < self._CONTROLLER_ANALOG_MIDDLE_VAL - self._CONTROLLER_ANALOG_DEADZONE_OFFSET:
            throttle = (-(e.state - self._CONTROLLER_ANALOG_MIDDLE_VAL)/self._CONTROLLER_ANALOG_MIDDLE_VAL) * 100
            direction = 1
            #print('Set Throttle: ', self.throttle)
        elif e.state > self._CONTROLLER_ANALOG_MIDDLE_VAL + self._CONTROLLER_ANALOG_DEADZONE_OFFSET:
            throttle = ((e.state - self._CONTROLLER_ANALOG_MIDDLE_VAL)/(self._CONTROLLER_ANALOG_MIDDLE_VAL+1)) * 100
            direction = 0
            #print('Set Throttle: ', self.throttle)
        else:
            throttle = 0
            direction = self.actuator.direction
        self.actuator.actuate(
            direction,
            throttle,
            self.actuator.turnAngle,
            self.actuator.brake,
            self
            )
    def steadyThrottle(self,e):
        if e.state == 1:
            self.actuator.actuate(
                self.actuator.direction,
                100,
                self.actuator.turnAngle,
                0,
                self
            )
        elif e.state == 0:
            self.actuator.actuate(
                self.actuator.direction,
                0,
                self.actuator.turnAngle,
                0,
                self
            )
    def processBrake(self,e):
        #print('Toggling Brake')
        if e.state == 1:
            brake = False if self.actuator.brake else True
            self.actuator.actuate(
                self.actuator.direction,
                self.actuator.throttle,
                self.actuator.turnAngle,
                brake,
                self
            )

    def processTurn(self,e):
        #print('Turning Angle: ', e.state)
        turnAngle = ((e.state/255) * 180) - 90
        self.actuator.actuate(
            self.actuator.direction,
            self.actuator.throttle,
            turnAngle,
            self.actuator.brake,
            self
        )


    def processExit(self,e):
        print('exiting')
    
    def processToggleAuto(self,e):
        if e.state == 1:
            if self.top.autopilot == True:
                self.top.DA_obj.exit()
            self.top.autopilot = not self.top.autopilot
    
    def processDriftRight(self,e):
        if e.state == 1:
            self.top.autoActuator.drift_right_manual()


    def processRecord(self,e):
        if e.state == 1:
            self.top.recorder.toggleRecording()

    def exit(self):
        print('Closing Joycon Thread')
        self.isExit = True
    

    def run(self):
        print('Joycon Thread Started')
        self.disabled = False
        while not self.isExit:
            events = get_gamepad()
            for event in events:
                #print(event.code)
                self.processEvent(event)
        print('Joycon Thread Closed!')