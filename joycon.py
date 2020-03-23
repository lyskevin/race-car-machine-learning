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




    def __init__(self, actuator):
        self.isExit = False
        self.controlMode = 'Manual'
        self.actuator = actuator
        self.recorder = None

        self.direction = 1 #1 = Forward | 0 = Backward
        self.throttle = 0 
        self.turnAngle= 0 
        self.brake = False

        self.recording =False

        self._ButtonHandlersNormal ={
            #### ANALOG STICKS ####
            "ABS_X": self.processTurn,
            "ABS_Y": self.nullControl,
            "ABS_Z": self.nullControl,
            "ABS_RZ": self.processThrottle,

            #### ABXY Buttons ####
            "BTN_EAST": self.nullControl,
            "BTN_SOUTH": self.nullControl,
            "BTN_NORTH": self.stop,
            "BTN_C": self.nullControl,

            #### DPAD ####
            "ABS_HAT0Y": self.nullControl,
            "ABS_HAT0X": self.nullControl,

            #### Bumper ####
            "BTN_Z": self.processBrake,
            "BTN_WEST": self.nullControl,
            "BTN_TR": self.nullControl,
            "BTN_TL": self.nullControl,

            #### Start ####
            "BTN_TR2": self.processRecord,
            "BTN_TL2": self.nullControl,
        }
        self.handlers = self._ButtonHandlersNormal



    def processEvent(self,e):
        if e.ev_type == 'Key' or e.ev_type == 'Absolute':
            hdlr = self.handlers.get(e.code)
            if not hdlr is None:
                hdlr(e)
                if self.controlMode == "Manual":
                    self.actuator.actuate(self.direction,self.throttle,self.turnAngle,self.brake)
        
    def nullControl(self,e):
        return None

    def processThrottle(self,e):
        #print('Set Throttle: ', e.state)
        if e.state < self._CONTROLLER_ANALOG_MIDDLE_VAL - self._CONTROLLER_ANALOG_DEADZONE_OFFSET:
            self.throttle = (-(e.state - self._CONTROLLER_ANALOG_MIDDLE_VAL)/self._CONTROLLER_ANALOG_MIDDLE_VAL) * 100
            self.direction = 1
            #print('Set Throttle: ', self.throttle)
        elif e.state > self._CONTROLLER_ANALOG_MIDDLE_VAL + self._CONTROLLER_ANALOG_DEADZONE_OFFSET:
            self.throttle = ((e.state - self._CONTROLLER_ANALOG_MIDDLE_VAL)/(self._CONTROLLER_ANALOG_MIDDLE_VAL+1)) * 100
            self.direction = 0
            #print('Set Throttle: ', self.throttle)
        else:
            self.throttle = 0


    def processBrake(self,e):
        #print('Toggling Brake')
        if e.state == 1:
            self.brake = False if self.brake else True

        
    def processRevese(self,e):
        #print('Changing Direction')
        if e.state == 1:
            self.direction = 1 if self.direction==0 else 0


    def processTurn(self,e):
        #print('Turning Angle: ', e.state)
        self.turnAngle = ((e.state/255) * 180) - 90


    def processExit(self,e):
        print('exiting')

    def processRecord(self,e):
        if e.state == 1 and self.recording == 0:
            self.recording = self.recorder.startRecording()
        elif  e.state == 1 and self.recording == 1:
            self.recorder.stopRecording()
            self.recording = False
        return None

    def stop(self,e):
        self.isExit = True

    def printState(self):
        print("Dir: ",self.direction," Pwr: ",self.throttle, " AGL: ", self.turnAngle, " Brake: ",self.brake )

    def getControlState(self):
        return (
            self.direction, #1 = Forward | 0 = Backward
            self.throttle, 
            self.turnAngle, 
            self.brake)
    def exit(self):
        print('Closing Joycon Thread')
        self.isExit = True
    
    def setRecorder(self, rec):
        self.recorder = rec

    def run(self):
        print('Joycon Thread Started')
        while not self.isExit:
            events = get_gamepad()
            for event in events:
                #print(event.code)
                self.processEvent(event)
        print('Joycon Thread Closed!')