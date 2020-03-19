import os
import pathlib
import numpy as np
import six.moves.urllib as urllib
import sys
import tarfile
import tensorflow as tf
import zipfile

from collections import namedtuple
from io import StringIO
from matplotlib import pyplot as plt
from PIL import Image
from IPython.display import display

import cv2
import time
import queue
import threading

from object_detection.utils import ops as utils_ops
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util

import triangulate
import decision_making
import socket_client


# patch tf1 into `utils.ops`
utils_ops.tf = tf.compat.v1
# Patch the location of gfile
tf.gfile = tf.io.gfile

gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
  try:
    # Currently, memory growth needs to be the same across GPUs
    for gpu in gpus:
      tf.config.experimental.set_memory_growth(gpu, True)
    logical_gpus = tf.config.experimental.list_logical_devices('GPU')
    print(len(gpus), "Physical GPUs,", len(logical_gpus), "Logical GPUs")
  except RuntimeError as e:
    # Memory growth must be set before GPUs have been initialized
    print(e)


def load_model(model_name):
  base_url = 'http://download.tensorflow.org/models/object_detection/'
  model_file = model_name + '.tar.gz'
  model_dir = tf.keras.utils.get_file(
    fname=model_name, 
    origin=base_url + model_file,
    untar=True)

  model_dir = pathlib.Path(model_dir)/"saved_model"

  model = tf.saved_model.load(str(model_dir))
  model = model.signatures['serving_default']

  return model

# List of the strings that is used to add correct label for each box.
PATH_TO_LABELS = os.path.join('data', 'mscoco_label_map.pbtxt')
category_index = label_map_util.create_category_index_from_labelmap(PATH_TO_LABELS, use_display_name=True)

def run_inference_for_single_image(model, image, filter_person=True):
  image = np.asarray(image)
  # The input needs to be a tensor, convert it using `tf.convert_to_tensor`.
  input_tensor = tf.convert_to_tensor(image)
  # The model expects a batch of images, so add an axis with `tf.newaxis`.
  input_tensor = input_tensor[tf.newaxis,...]

  # Run inference
  output_dict = model(input_tensor)

  # All outputs are batches tensors.
  # Convert to numpy arrays, and take index [0] to remove the batch dimension.
  # We're only interested in the first num_detections.
  num_detections = int(output_dict.pop('num_detections'))
  # output_dict = {key:value[0, :num_detections].numpy() 
  #                for key,value in output_dict.items()}
  indices = np.where(output_dict['detection_classes'][0, :num_detections].numpy() == 1)

  for key,value in output_dict.items():
    value_np = value[0, :num_detections].numpy()
    output_dict[key] = value_np[indices]
  output_dict['num_detections'] = num_detections

  # detection_classes should be ints.
  output_dict['detection_classes'] = output_dict['detection_classes'].astype(np.int64)
   
  # Handle models with masks:
  if 'detection_masks' in output_dict:
    # Reframe the the bbox mask to the image size.
    detection_masks_reframed = utils_ops.reframe_box_masks_to_image_masks(
              output_dict['detection_masks'], output_dict['detection_boxes'],
               image.shape[0], image.shape[1])      
    detection_masks_reframed = tf.cast(detection_masks_reframed > 0.5,
                                       tf.uint8)
    output_dict['detection_masks_reframed'] = detection_masks_reframed.numpy()
    
  return output_dict


def show_inference(model, image_np):
  # the array based representation of the image will be used later in order to prepare the
  # result image with boxes and labels on it.
  # Actual detection.
  output_dict = run_inference_for_single_image(model, image_np)
  # Visualization of the results of a detection.
  vis_util.visualize_boxes_and_labels_on_image_array(
      image_np,
      output_dict['detection_boxes'],
      output_dict['detection_classes'],
      output_dict['detection_scores'],
      category_index,
      instance_masks=output_dict.get('detection_masks_reframed', None),
      use_normalized_coordinates=True,
      line_thickness=8)

  return image_np, output_dict


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

# cv2 display preferences
font = cv2.FONT_HERSHEY_SIMPLEX
fpsPosition = (10, 100)
fontScale = 0.5
fontColor = (255, 255, 255)
lineType = 2

def displayFps(image, start_time):
  fps = 1 / (time.time() - start_time)
  info = f"{fps} fps"
  
  cv2.putText(image, info,
              fpsPosition,
              font,
              fontScale,
              fontColor,
              lineType)
  return fps

def getMiddleCoordinates(image, output_dict, width, height, min_score_thresh=.5, display=True):
  boxes = output_dict['detection_boxes']
  classes = output_dict['detection_classes']
  scores = output_dict['detection_scores']
  coordinatesList = []
  
  TextYCoordinate = 150
  for i in range(boxes.shape[0]):
    if scores is None or scores[i] > min_score_thresh:
      ymin = round(boxes[i,0]*height, 2)
      xmin = round(boxes[i,1]*width, 2)
      ymax = round(boxes[i,2]*height, 2)
      xmax = round(boxes[i,3]*width, 2)
      xmid = int((xmin + xmax) / 2)
      ymid = int((ymin + ymax) / 2)
      midCoordinate = (xmid, ymid)
      coordinatesList.append(midCoordinate)

      belowTimeText = (10,TextYCoordinate)
      cv2.putText(image, f'{midCoordinate}', 
                  belowTimeText,
                  font,
                  fontScale,
                  fontColor,
                  lineType)
      cv2.putText(image, "X", 
                  midCoordinate, 
                  font, 
                  fontScale,
                  (0,0,255),
                  lineType)
      TextYCoordinate += 50

  return coordinatesList
  

# distance calculation parameters initialization
width = 640
height = 480
# angle_width=62.2 # rpi cam
angle_width=66 # kyle
angler = triangulate.Frame_Angles(width,height,angle_width)
angler.build_frame()
# camera_distance = 0.15 # rpi cam
camera_distance = 0.16 #kyle

# calculate distance from phone to detected object
def distance_calculation(left_coordinate, right_coordinate):
  (xlp, ylp) = left_coordinate
  (xrp, yrp) = right_coordinate
  xlangle,ylangle = angler.angles_from_center(xlp,ylp,top_left=True,degrees=True)
  xrangle,yrangle = angler.angles_from_center(xrp,yrp,top_left=True,degrees=True)
  X,Y,Z,D = angler.location(camera_distance,(xlangle,ylangle),(xrangle,yrangle),center=True,degrees=True)

  return D

# initializing rc car control
transmission_delay=0.02
slow_dist=1
brake_dist=0.5
max_speed=0.83
frames_to_skip=0
waiting_time=1
driver = decision_making.Drive(
    transmission_delay=transmission_delay,
    slow_dist=slow_dist,
    brake_dist=brake_dist,
    max_speed=max_speed,
    frames_to_skip=frames_to_skip,
    waiting_time=waiting_time)

def speed_calculation(fps, distance):
  speed = driver.accelerate(fps, distance)
  return speed

# initializing socket client
host = '127.0.0.1'
port = 9999
socket = socket_client.Socket(host,port)

def getAvgTimeDelay(start_time, avg_delay=0, acc=0):
  # elapsed time is in ms
  elapsed_time = (time.time() - start_time) * 1000
  new_acc = acc + 1
  new_avg_delay = (( avg_delay*(acc) ) + elapsed_time) / new_acc

  return new_avg_delay, new_acc


# ip_left = 0  # Use this only if you have one webcam for testing
# ip_left = "http://192.168.43.190/?action=stream"
# ip_right = "http://192.168.43.22/?action=stream"
ip_left = "http://192.168.43.1:8080/video"
ip_right = "http://192.168.43.41:8080/video"
cap_left = VideoCapture(ip_left)
cap_right = VideoCapture(ip_right)
# cap_right = cap_left

# Models can be found here: https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/detection_model_zoo.md
model_name = 'ssdlite_mobilenet_v2_coco_2018_05_09'
detection_model = load_model(model_name)
avg_delay = 0
acc = 0

while True:
    start_time = time.time()

    # Read frame from camera
    image_np_left = cap_left.read()
    image_np_right = cap_right.read()

    image_np_left, output_dict_left = show_inference(detection_model, np.array(image_np_left))
    image_np_left = cv2.resize(image_np_left, (width, height))
    coords_left = getMiddleCoordinates(image_np_left, output_dict_left, width, height)

    image_np_right, output_dict_right = show_inference(detection_model, np.array(image_np_right))
    image_np_right = cv2.resize(image_np_right, (width, height))
    fps = displayFps(image_np_right, start_time)
    coords_right = getMiddleCoordinates(image_np_right, output_dict_right, width, height)

    distance = None
    if coords_left and coords_right:
      distance = distance_calculation(coords_left[0], coords_right[0])
      print(f"distance: {distance}")
    
    speed = speed_calculation(fps, distance)
    print(f"speed: {speed}")

    # send speed to socket server
    socket.send(speed)

    # Display output
    results = np.concatenate((image_np_left, image_np_right), axis=1)
    cv2.imshow('object detection', results)
    
    # avg_delay, acc = getAvgTimeDelay(start_time, avg_delay, acc)
    # print(avg_delay)

    if cv2.waitKey(25) & 0xFF == ord('q'):
        cv2.destroyAllWindows()
        socket.close()
        break
