import numpy as np
import io
import picamera
import time
import os
import threading
from PIL import Image

class recorder:
    def __init__(self):
        self.modes = {"continuousCapture": self.captureContinuous, "captureOnChange": self.captureOnChange}
        self.mode = "continuousCapture"
        self.settings = {"sessionNameAutomatic":True}
        self.recoderInput = None
        self.cameraHot = False
        self.sysExit = False
        self.sessionName = None

        ##making sure the sessions folder is there##
        l = os.listdir()
        if not 'sessions' in l:
            os.mkdir("sessions")
            print("created sessions folder")

    def setTop(self,top):
        self.top = top
        self.recoderInput = top.actuator
        
    def constructFilename(self,i,params):
        direction,throttle,turnAngle,brake = params
        if not direction:
            throttle = 0
        filename = str(i) + "_" + str(round(throttle)) + "_" + str(round(turnAngle))+ "_" + str(brake) + ".jpg"
        return os.path.join(".","sessions",self.sessionName,filename)


    def captureContinuous(self):
        print("captureContinuous")
        with picamera.PiCamera(resolution=(640, 480), framerate=30) as camera:
            os.mkdir("./sessions/"+ self.sessionName)
            stream = io.BytesIO()
            pic = 0
            avgFps = 0
            start_time = time.time()
            for _ in camera.capture_continuous(stream, format='jpeg', use_video_port=True):
                # Truncate the stream to the current position (in case
                # prior iterations output a longer image)

                stream.seek(0)
                filename = self.constructFilename(pic,self.recoderInput.getControlState())
                pic+=1
                Image.open(stream).save(filename,format = 'jpeg')
                avgFps = pic/(time.time() - start_time)
                stream.seek(0)
                stream.truncate()
                if self.cameraHot == False or self.sysExit:
                    break
            self.cameraHot = False
            print("done! avgFps = {}".format(avgFps))


    def captureOnChange(self):
        print("captureOnChange")
        with picamera.PiCamera(resolution=(640, 480), framerate=30) as camera:
            os.mkdir("./sessions/"+ self.sessionName)
            stream = io.BytesIO()
            pic = 0
            
            prev = self.recoderInput.getControlState()
            for _ in camera.capture_continuous(stream, format='jpeg', use_video_port=True):
                # Truncate the stream to the current position (in case
                # prior iterations output a longer image)
                stream.seek(0)
                if self.recoderInput.getControlState() == prev:
                    stream.seek(0)
                    stream.truncate()
                    if self.cameraHot == False or self.sysExit:
                        break
                    continue
                filename = self.constructFilename(pic,self.recoderInput.getControlState())
                prev = self.recoderInput.getControlState()
                pic+=1
                Image.open(stream).save(filename,format = 'jpeg')
                stream.seek(0)
                stream.truncate()
                if self.cameraHot == False or self.sysExit:
                    break
            self.cameraHot = False
            print("done! Took{} samples".format(pic))



            

    def run(self):
        print("Camera Thread Started")
        while not self.sysExit:
            if (self.cameraHot) and (not self.mode == None):
                self.modes[self.mode]()
        print("Camera Thread closed!")

    
    def startRecording(self):
        #probably could use a lock here but wtv doesnt matter that much
        if self.cameraHot == True:
            print("Session Already Running")
            return False
        if self.sessionName == None:
            if self.settings["sessionNameAutomatic"]:
                sessions = list(filter(lambda x: "test_" in x,os.listdir("./sessions")))
                if len(sessions) == 0:
                    print("Setting Session Name as test_0")
                    self.sessionName = "test_0"
                else:
                    sessions_num = max(list(map(lambda x: int(x.split("test_")[1]),sessions)))+1
                    self.sessionName = "test_" + str(sessions_num)
                    print("Setting Session Name as " + self.sessionName )
            else:
                print("Please set SessionName")
                return False
        sessions = os.listdir("./sessions")
        if self.sessionName in sessions:
            if self.settings["sessionNameAutomatic"]:
                sessions = list(filter(lambda x: "test_" in x,os.listdir("./sessions")))
                sessions_num = max(list(map(lambda x: int(x.split("test_")[1]),sessions)))+1
                self.sessionName = "test_" + str(sessions_num)
                print("Setting Session Name as " + self.sessionName )
            else:
                print("Session Name Taken. Use another")
                return False
        print("starting Recording: {}".format(self.sessionName))
        self.cameraHot = True
        return True
    
    def stopRecording(self):
        print("Ending Recording: Session{}".format(self.sessionName))
        self.cameraHot = False

    def toggleRecording(self):
        if self.cameraHot:
            self.stopRecording()
        else:
            self.startRecording()

    def setSessionName(self, n):
        if self.cameraHot:
            print("Unable to set name! Recording in Progress")
        if "test_" in n:
            print("'test_' is reserved. Use another")
        self.sessionName = n
        print("SessionName Set as {}".format(n))

    def setSetting(self, settingName, settingValue):
        if not (settingName in self.settings.keys()):
            print("Cannot set settngs. Invalid Setting")
        elif not (settingValue in ["True", "False"] ):
            print("Cannot set settngs. Invalid Value for setting: " + settingName)
        else:
            self.settings[settingName] = settingValue == "True"

    def exit(self):
        print('Closing Camera Thread')
        self.sysExit = True
    
# r = recorder()
# r.setSessionName("dasdingo")
# r.startRecording()
# mythread = threading.Thread(target= r.mainloop)
# mythread.start()
# a = input()
# r.sysExit = True
