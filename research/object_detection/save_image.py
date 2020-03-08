import cv2
import queue
import threading

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
cap = VideoCapture("http://192.168.0.126:8080/video")  # access IP camera from android phone
i = 0

while True:
	frame = cap.read()

	cv2.imshow('object detection right', frame)
	if cv2.waitKey(25) & 0xFF == ord('s'):
		cv2.imwrite(f"right_photos/right_{i}.jpg", frame)
		i += 1

	elif cv2.waitKey(25) & 0xFF == ord('q'):
		cv2.destroyAllWindows()
		break