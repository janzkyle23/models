import socket
import time

class Socket:
    def __init__(self,host='127.0.0.1',port=9999):
        # create a socket object
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # connection to hostname on the port.
        self.s.connect((host, port))
        print(f"connected to {host}:{port}")
        # initialize ESC of RC car
        time.sleep(1)
        msg = "init"
        self.s.send(msg.encode('ascii'))
        time.sleep(3)

    def send(self, speed):
        msg = "%0.2f" % speed
        print(msg)
        self.s.send(msg.encode('ascii'))
        print(f"sent: {msg}")
        time.sleep(0.0001)

    def close(self):
        self.s.close()