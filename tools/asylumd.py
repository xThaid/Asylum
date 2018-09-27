import serial
import socket
import sys
import os
import jsonrpc
import config

from concurrent.futures import ThreadPoolExecutor

SHUTTER_REPEAT_COUNT = 5
GATE_REPEAT_COUNT = 3


class Arduino:
    def __init__(self):
        try:
            self.serial = serial.Serial("/dev/serial0", 115200, timeout=1)
        except serial.SerialException:
            print("Failed to open serial port")
            sys.exit(1)

    def ping(self):
        data = "0"
        self.serial.write((data + '\n').encode())
        print(self.serial.readline())

    def shutterAction(self, id, action, repeatCount=SHUTTER_REPEAT_COUNT):
        print("shutter " + id + " " + action)
        data = "1"
        data += (str(id))
        data += (str(action))
        data += (str(repeatCount))
        self.serial.write((data + '\n').encode())
        print(self.serial.readline())
        print(self.serial.readline())

    def gateAction(self, id, repeatCount=GATE_REPEAT_COUNT):
        print("gate " + id)
        data = "2"
        data += (str(id))
        data += (str(repeatCount))
        self.serial.write((data + '\n').encode())
        print(self.serial.readline())
        print(self.serial.readline())


class Server:
    def __init__(self, socket_loc):
        if(os.path.exists(socket_loc)):
            os.remove(socket_loc)

        self.executor = ThreadPoolExecutor(max_workers=1)
        self.service = jsonrpc.JsonRpcService()

        self.server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.server.bind(socket_loc)

    def addMethod(self, f, is_notification=False):
        def decorated_function(*args, **kwargs):
            future = self.executor.submit(f, *args, **kwargs)
            if not is_notification:
                return future.result()
            return None

        self.service.add_method(decorated_function, f.__name__)

    def serve(self):
        self.server.listen(1)
        while True:
            conn, addr = self.server.accept()
            self.handleConnection(conn)

    def handleConnection(self, conn):
        data = conn.recv(1024)
        resp = self.service.handle(data)
        if resp is not None:
            conn.send(resp.json().encode())
        conn.close()


def main():
    arduino = Arduino()
    server = Server(config.config['ASYLUMD']['socket_loc'])
    server.addMethod(arduino.ping)
    server.addMethod(arduino.shutterAction, True)
    server.addMethod(arduino.gateAction, True)
    server.serve()


if __name__ == '__main__':
    main()
