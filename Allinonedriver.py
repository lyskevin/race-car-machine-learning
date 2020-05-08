import numpy as np
import io
import picamera
import time

from PIL import Image
from tflite_runtime.interpreter import Interpreter
import cv2


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
        self._interpreter = Interpreter("./reducedSizenoOOB.tflite")
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
            img = normalize(img)
            return img
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
                    image = image_preprocess(image)
                    img = image[np.newaxis, ...]
                    input_data = np.array(img, dtype=np.float32)
                    self._interpreter.set_tensor(input_details[0]['index'], input_data)

                    self._interpreter.invoke()
                    output_data = self._interpreter.get_tensor(output_details[0]['index'])[0]
                    time_taken_ms = (time.time() - start_time) * 1000
                    desc =self.descs[np.argmax(output_data, axis=None, out=None)]
                    if desc == 'drift':
                        self.driftcount+=1
                        if self.driftcount > 1:
                            if self.driftcycle:
                                act.drift_right_manual()
                            else:
                                act.drift_right_manual2()
                            self.driftcycle = not self.driftcycle
                            self.driftcount =0
                    #descs = ["right","left", "straight",'drift','oob']
                    elif desc == "right":
                        act.correct_right()
                        self.driftcount =0
                    elif desc == "left":
                        act.correct_left()
                        self.driftcount =0
                    elif desc == "straight":
                        act.straight()
                        self.driftcount =0
                    print(f'output_data:{desc}, time_taken:{time_taken_ms}ms')
                    camera.annotate_text = str(output_data) + ", " + str(time_taken_ms)
                    stream.seek(0)
                    stream.truncate()
                    if self.is_exit:
                        break
              
            except KeyboardInterrupt:
                print("DriveAgent: Ctrl-C")
            finally:
                print("DriveAgent: done")


