import socket
import time

class Socket:
    def __init__(self,host='127.0.0.1',port=9999):
        # create a socket object
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        host = '127.0.0.1'
        port = 9999

        # connection to hostname on the port.
        self.s.connect((host, port))
        print(f"connected to {host}:{port}")
        # initialize ESC of RC car
        msg = "init"
        self.s.send(msg.encode('ascii'))

    def send(self, speed):
        msg = str(speed)
        self.s.send(msg.encode('ascii'))
        print(f"sent: {msg}")

    def close(self):
        self.s.close()