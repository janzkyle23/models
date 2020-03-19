import os     #importing os library so as to communicate with the system
import time   #importing time library to make Rpi wait because its too impatient 
time.sleep(1) # As i said it is too impatient and so if this delay is removed you will get an error
import socket
import queue
import threading


max_value = 1675 #change this if your ESC's max value is different or leave it be
min_value = 1500  #change this if your ESC's min value is different or leave it be
accelerate_value = 1800
brake_value = 1300

actual_max_speed = 0.83 # m/s

class DataCapture:
  
   def __init__(self):
      self.conn, self.addr = serv.accept()
      self.q = queue.Queue()
      t = threading.Thread(target=self._reader)
      t.daemon = True
      t.start()

   # read data as soon as they are available, keeping only most recent one
   def _reader(self):
      while True:
         data = self.conn.recv(1024)
         if not data:
            self.q.put(data)
            break
         if not self.q.empty():
            try:
               self.q.get_nowait()   # discard previous (unprocessed) frame
            except Queue.Empty:
               pass
         self.q.put(data)

   def recv(self):
      return self.q.get()

   def close(self):
      self.conn.close()


def arm(): #This is the arming procedure of an ESC 
   print("RPI is arming")
   time.sleep(3)

def start_up():
   print(f"accelerating: {accelerate_value}")
   time.sleep(0.3)

def set_speed(speed):
   #TODO interpolate speed values to the corresponding input values by ESC
   span = max_value - min_value

   # Convert the left range into a 0-1 range (float)
   value_scaled = speed / actual_max_speed

   # Convert the 0-1 range into a value in the right range.
   output = int((value_scaled * span) + min_value)
   
   print (f"speed: {speed}; output: {output}")

def full_brake():
   print (f"brake: {brake_value}")

def stop(): #This will stop every action your Pi is performing for ESC ofcourse.
   print("stopping RPI")

serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serv.bind(('0.0.0.0', 9999))
serv.listen(5)

while True:
   conn = DataCapture()
   start_up_toggle = True
   is_stopped = True

   while True:
      print ("Initializing...")
      data = conn.recv()
      if not data: break
      if data.decode('ascii') == "init":
         arm()
         start_up_toggle = True
         break

   while True:
      data = conn.recv()
      if not data: break

      speed = float(data.decode('ascii'))

      if start_up_toggle and speed > 0:
         start_up()
         start_up_toggle = False
         is_stopped = False
      
      if speed == 0:
         start_up_toggle = True
         if not is_stopped:
            full_brake()
            is_stopped = True
      
      set_speed(speed)

   if not is_stopped:
      full_brake()
   conn.close()
   print ('client disconnected')

stop()