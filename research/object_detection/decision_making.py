# set variables
max_speed = 2.78 #m/s
stop_dist = 0.5 #m
transmission_delay = 0.02 #s

#output values by system
detection_fps = 10 #fps # = 1 / lag
curr_distance

#temp stored variables
prev_distance
prev_true_speed
prev_acceleration

#calculated variables
curr_relative_speed
curr_true_speed
curr_true_distance
acceleration

if curr_distance and not prev_distance:
  if curr_distance <= stop_dist:
    stop()
  else:
    applyPrevAcceleration()

elif prev_distance and not curr_distance:
  applyPrevAcceleration()

elif not curr_distance and not prev_distance:
	if prev_acceleration == 0:
		curr_true_speed = max_speed
	else:
		applyPrevAcceleration()

else:
  curr_relative_speed = detection_fps * (prev_distance - curr_distance)
  true_curr_distance = curr_distance + (curr_relative_speed * transmission_delay)

	if true_curr_distance <= stop_dist:
		stop()
	else:
		