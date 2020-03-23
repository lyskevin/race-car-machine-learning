import numpy as np
import io
import picamera
import time
import os
import threading
from PIL import Image

class recorder:
    def __init__(self,controller):
        self.controller = controller
        self.cameraHot = False
        self.sysExit = False
        self.sessionName = None

        ##making sure the sessions folder is there##
        l = os.listdir()
        if not 'sessions' in l:
            os.mkdir("sessions")
            print("created sessions folder")
    def constructFilename(self,i,params):
        direction,throttle,turnAngle,brake = params
        if not direction:
            throttle = 0
        filename = str(i) + "_" + str(round(throttle)) + "_" + str(round(turnAngle))+ "_" + str(brake) + ".jpg"
        return os.path.join(".","sessions",self.sessionName,filename)

    def run(self):
        print("Camera Thread Started")
        while not self.sysExit:
            while (not self.cameraHot) and not self.sysExit:
                pass
            if self.sysExit:
                break
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
                    filename = self.constructFilename(pic,self.controller.getControlState())
                    pic+=1
                    Image.open(stream).save(filename,format = 'jpeg')
                    avgFps = pic/(time.time() - start_time)
                    stream.seek(0)
                    stream.truncate()
                    if self.cameraHot == False or self.sysExit:
                        break
                self.cameraHot = False
                print("done! avgFps = {}".format(avgFps))
        print("Camera Thread closed!")
    
    def startRecording(self):
        #probably could use a lock here but wtv doesnt matter that much
        if self.cameraHot == True:
            print("Session Already Running")
            return False
        if self.sessionName == None:
            print("Please set SessionName")
            return False
        sessions = os.listdir("./sessions")
        if self.sessionName in sessions:
            print("Session Name Taken. Use another")
            return False
        print("starting Recording: Session{}".format(self.sessionName))
        self.cameraHot = True
        return True
    
    def stopRecording(self):
        print("Ending Recording: Session{}".format(self.sessionName))
        self.cameraHot = False

    def setSessionName(self, n):
        if self.cameraHot:
            print("Unable to set name! Recording in Progress")
        self.sessionName = n
        print("SessionName Set as {}".format(n))

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
