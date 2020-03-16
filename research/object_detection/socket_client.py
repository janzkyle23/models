import socket
import time

# create a socket object
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# get local machine name
host = '192.168.0.105'

port = 9999

# connection to hostname on the port.
s.connect((host, port))

while True:
    time.sleep(1)
    msg = "Hello\r\n"                           
    s.send(msg.encode('ascii'))
    # Receive no more than 1024 bytes
    msg = s.recv(1024)                                     

s.close()
print (msg.decode('ascii'))