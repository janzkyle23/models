class Drive:
  transmission_delay = 0.02 #s; video transmission delay from rpi to server/PC
  stop_dist = 1 #m
  max_speed = 0.83 #m/s
  frames_to_skip = 0 # set if the user wants to skip frames
  waiting_time = 1 #s; how long system should wait to make sure that no object is in front before moving forward 

  #temp stored variables
  prev_distance = None
  prev_true_speed = 0
  elapsed_waiting_time = 0

  def __init__(
      self,
      transmission_delay=0.02,
      stop_dist=1,
      max_speed=0.83,
      frames_to_skip=0
      waiting_time=1):
    if type(transmission_delay) in (int,float):
      self.transmission_delay = float(transmission_delay)
    if type(stop_dist) in (int,float):
      self.stop_dist = float(stop_dist)
    if type(max_speed) in (int,float):
      self.max_speed = float(max_speed)
    if type(frames_to_skip) in (int,float):
      self.frames_to_skip = int(frames_to_skip)
    if type(waiting_time) in (int,float):
      self.waiting_time = float(waiting_time)


  def accelerate(self, detection_fps, curr_distance=None):
    detection_fps = detection_fps / (frames_to_skip + 1)
    output_speed = 0

    if not curr_distance and not prev_distance:
      # ensure that there's no object detected for waiting_time secs before returning max_speed
      if elapsed_waiting_time >= waiting_time:  
        elapsed_waiting_time = 0
        print("gotta blast")
        output_speed = max_speed
      else:
        elapsed_waiting_time += 1 / detection_fps
        output_speed = prev_true_speed

    elif not curr_distance or not prev_distance:
      output_speed = prev_true_speed

    else:
      # current relative speed should be positive if car is approaching the object
      curr_relative_speed = detection_fps * (prev_distance - curr_distance)
      # considering the transmission delay to reevaluate the current distance of object
      true_curr_distance = curr_distance - (curr_relative_speed * transmission_delay)

      if true_curr_distance <= stop_dist:
        if curr_relative_speed >= 0:
          print("slowing down")
          output_speed = prev_true_speed-curr_relative_speed
        else:
          output_speed = prev_true_speed

      else:
        print("gotta blast")
        output_speed = max_speed
    
    # make sure that output speed is always 0 or positive
    output_speed = max(0, output_speed)

    # storing values for next loop
    self.prev_distance = curr_distance
    self.prev_true_speed = output_speed

    return output_speed
