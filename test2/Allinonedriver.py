import numpy as np
import io
import picamera
import time

from PIL import Image
from tflite_runtime.interpreter import Interpreter
import cv2
from math import atan,degrees


def normalize(img):
  img = np.divide(img, 255)
  img = np.subtract(img, 0.5)
  return img
def denormalize(img):
  img = np.add(img, 0.5)
  return img

def convert_opencv(image): #picam comes out BGR
    im = np.array(image) 
    return im

def image_preprocess(img):
  img = convert_opencv(img)
  height, a, b = img.shape
  img = img[int(height/2)+50:,:,:]
  img = cv2.resize(img, None, fx = 0.6, fy = 0.6)
  img = normalize(img)
  return img

class DriveAgent:
    descs = ["right","left", "straight",'drift','oob']
    def __init__(self, top):
        self.is_exit = False
        self.driftcount = 0
        self.driftcycle = True
        self.driftTimeout=0
        self.straightCount = 0
        self._interpreter = Interpreter("./reducedSizenoOOB2.tflite")
        self._interpreter.allocate_tensors()

        print(self._interpreter.get_input_details())
        print(self._interpreter.get_output_details())
        _, self._input_height, self._input_width, _ = self._interpreter.get_input_details()[0]['shape']
        print(self._input_height)
        print(self._input_width)
        self.top = top
    def run(self):
        self.main()

    def exit(self):
        self.is_exit = True

    def main(self):
        def slope(x1, y1, x2, y2):
            return (y2-y1)/(x2-x1)
        def hough(img):
            gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
            rc, gray = cv2.threshold(gray, 60, 255, cv2.THRESH_BINARY_INV)
            h,w = gray.shape
            cv2.rectangle(gray, (0,h-20), (w,h), 0, thickness = -1)
            edges = cv2.Canny(gray,1,255,apertureSize = 3)
            minLineLength = 30
            maxLineGap = 2
            lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 50, None, minLineLength, maxLineGap)
            if lines is None:
                return False
            for x1,y1,x2,y2 in lines[0]:
                gradient = slope(x1, y1, x2, y2)
                angle = round(degrees(atan(gradient)))
                print(angle)
            return (angle > 0 and angle < 40)
        def image_preprocess(img): 
            def normalize(img):
                img = np.divide(img, 255)
                img = np.subtract(img, 0.5)
                return img
            def denormalize(img):
                img = np.add(img, 0.5)
                return img

            def convert_opencv(image): #picam comes out BGR
                im = np.array(image) 
                return im
            img = convert_opencv(img)
            height, a, b = img.shape
            img = img[int(height/2)+50:,:,:]
            img = cv2.resize(img, None, fx = 0.6, fy = 0.6)
            img_normal = normalize(img)
            return (img_normal,img)
        act = self.top.autoActuator
        input_details = self._interpreter.get_input_details()
        output_details = self._interpreter.get_output_details()
        with picamera.PiCamera(resolution=(640, 480), framerate=30) as camera:
            # camera.vflip = True
            # camera.start_preview()
            try:
                stream = io.BytesIO()
                for _ in camera.capture_continuous(stream, format='jpeg', use_video_port=True):
                    stream.seek(0)
                    start_time = time.time()
                    image = Image.open(stream).convert('RGB')
                    image,img_unprocessed = image_preprocess(image)
                    img = image[np.newaxis, ...]
                    input_data = np.array(img, dtype=np.float32)
                    self._interpreter.set_tensor(input_details[0]['index'], input_data)

                    self._interpreter.invoke()
                    output_data = self._interpreter.get_tensor(output_details[0]['index'])[0]
                    time_taken_ms = (time.time() - start_time) * 1000
                    desc_index = np.argmax(output_data, axis=None, out=None)
                    desc =self.descs[desc_index]
                    confidence = output_data[desc_index]
                    if desc == 'drift':
                        self.driftcount+=1
                        if self.driftTimeout < 1:
                            if self.driftcount > 0:
                                if self.driftcycle:
                                    act.drift_right_manual()
                                    
                                else:
                                    act.drift_right_manual2()
                                self.driftcycle = not self.driftcycle
                                self.driftcount =0
                                self.driftTimeout = 2
                                self.straightCount =0
                            else:
                                self.driftTimeout -=1
                                act.straight()
                                self.straightCount +=1
                        else:
                            self.driftTimeout -=1
                            if(hough(img_unprocessed)):
                                desc = "houghleft_Drift"
                                act.correct_left()
                            else:
                                desc = "straight_Drift"
                                act.straight()
                                self.straightCount +=1
                    #descs = ["right","left", "straight",'drift','oob']
                    elif self.straightCount >3:
                        self.driftcount+=1
                        if self.driftTimeout < 1:
                            if self.driftcount > 0:
                                if self.driftcycle:
                                    act.drift_right_manual()
                                    
                                else:
                                    act.drift_right_manual2()
                                self.driftcycle = not self.driftcycle
                                self.driftcount =0
                                self.driftTimeout = 2
                                self.straightCount =0
                            else:
                                self.driftTimeout -=1
                                act.straight()
                                self.straightCount +=1
                        else:
                            self.driftTimeout -=1
                            if(hough(img_unprocessed)):
                                desc = "houghleft_Drift"
                                act.correct_left()
                            else:
                                desc = "straight_Drift"
                                act.straight()
                                self.straightCount +=1
                    elif desc == "right":
                        act.correct_right()
                        self.driftcount =0
                    elif desc == "left":
                        # if(hough(img_unprocessed)):
                        #     desc = "houghleft_left"
                        #     act.correct_left()
                        # else:
                        #     desc = "rej_left"
                        #     act.straight()
                        act.correct_left()
                        self.driftcount =0
                    elif desc == "straight":
                        if(hough(img_unprocessed)):
                            desc = "houghleft"
                            act.correct_left()
                        else:
                            act.straight()
                            self.straightCount +=1
                        self.driftcount =0
                    print(f'output_data:{desc}, time_taken:{time_taken_ms}ms , confidence:{confidence}')
                    camera.annotate_text = str(output_data) + ", " + str(time_taken_ms)
                    stream.seek(0)
                    stream.truncate()
                    if self.is_exit:
                        break
              
            except KeyboardInterrupt:
                print("DriveAgent: Ctrl-C")
            finally:
                print("DriveAgent: done")


