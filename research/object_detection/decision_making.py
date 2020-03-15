# fixed variables
transmission_delay = 0.02 #s
analog_input = [0,1024]

# set variables
stop_dist = 0.5 #m
max_speed = 2.78 #m/s
max_acceleration = max_speed # 1 sec from 0 to max speed and vice versa
frames_to_skip = 0

#output values by system
detection_fps = 10 #fps # = 1 / lag
detection_fps = detection_fps / (frames_to_skip + 1)
curr_distance

#temp stored variables
prev_distance
prev_true_speed
prev_acceleration

#calculated variables
curr_relative_speed
curr_true_speed # always 0 or positive
true_curr_distance # approximate true distance of object when video transmission delay is considered 
acceleration

def applyPrevAcceleration():
  return self.prev_true_speed + (self.prev_acceleration / self.detection_fps)

if curr_distance and not prev_distance:
  if curr_distance <= stop_dist:
    stop()
  else:
    curr_true_speed = applyPrevAcceleration()

elif prev_distance and not curr_distance:
  curr_true_speed = applyPrevAcceleration()

elif not curr_distance and not prev_distance:
	if prev_acceleration == 0:
		curr_true_speed = max_speed
	else:
		curr_true_speed = applyPrevAcceleration()

else:
  curr_relative_speed = detection_fps * (prev_distance - curr_distance) # positive if car is approaching the object
  true_curr_distance = curr_distance - (curr_relative_speed * transmission_delay)

	if true_curr_distance <= stop_dist:
    if curr_relative_speed < 0:
      curr_true_speed = prev_true_speed
    else:
      curr_true_speed = prev_true_speed + curr_relative_speed # result is <= prev_true_speed

	elif curr_relative_speed <= 0: # check if object is getting far
    curr_true_speed = min(prev_true_speed-curr_relative_speed, max_speed)

  elif curr_relative_speed > 0: # if object is getting near
    curr_true_speed = min(prev_true_speed-curr_relative_speed, max_speed)
  
  curr_true_speed = max(0, curr_true_speed) # making sure that there's no negative speed

prev_distance = curr_distance
prev_acceleration = (curr_true_speed - prev_true_speed) * detection_fps
prev_true_speed = curr_true_speed

return curr_true_speed