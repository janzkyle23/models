import cv2
import numpy as np
import queue #experiment
import threading #experiment


# bufferless VideoCapture
class VideoCapture:

  def __init__(self, name):
    self.cap = cv2.VideoCapture(name)
    # self.cap.set(6, cv2.VideoWriter_fourcc('H', '2', '6', '4')) # for reading raspivid
    self.q = queue.Queue()
    t = threading.Thread(target=self._reader)
    t.daemon = True
    t.start()

  # read frames as soon as they are available, keeping only most recent one
  def _reader(self):
    while True:
      ret, frame = self.cap.read()
      if not ret:
        break
      if not self.q.empty():
        try:
          self.q.get_nowait()   # discard previous (unprocessed) frame
        except Queue.Empty:
          pass
      self.q.put(frame)

  def read(self):
    return self.q.get()

# load video streaming
cap = VideoCapture("http://192.168.0.125:8080/video")  # access IP camera from android phone
cap2 = VideoCapture("http://192.168.0.126:8080/video")  # access IP camera from android phone

while True:
    # load streams
    image_np = cap.read()
    image_np2 = cap2.read()

    # 1st video stream
    image_np = cv2.line(image_np, (0,240), (640,240), (0,0,255), 2)

    # 2nd video stream
    image_np2 = cv2.line(image_np2, (0,240), (640,240), (0,0,255), 2)
    
    # Display output
    results = np.concatenate((image_np, image_np2), axis=1)
    cv2.imshow('object detection right', results)

    if cv2.waitKey(25) & 0xFF == ord('q'):
        cv2.destroyAllWindows()
        break