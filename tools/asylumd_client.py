import jsonrpc
import socket
import sys

import config

socket_loc = config.config['ASYLUMD']['socket_loc']


def sendToServer(request):
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect(socket_loc)
    sock.sendall(request.json().encode())
    response = None
    if not request.is_notification:
        data = sock.recv(1024)
        response = jsonrpc.JsonRpcResponse.from_json(data.decode())
    sock.close()
    return response


def ping():
    req = jsonrpc.JsonRpcRequest(method="ping", id=0)
    print(sendToServer(req).result)


def shutterAction(id, action):
    if id < 0 or id > 8 or action < 0 or action > 2:
        return
    req = jsonrpc.JsonRpcRequest(
        method="shutterAction",
        params=[id, action])
    sendToServer(req)


def gateAction(id):
    if id < 0 or id > 3:
        return
    req = jsonrpc.JsonRpcRequest(
        method="gateAction",
        params=[id])
    sendToServer(req)


def main():
    if len(sys.argv) < 2:
            print("ardu.py ['ping'/'shutter'/'gate'] [id] [action]")
            sys.exit(1)
    if sys.argv[1] == 'ping':
        ping()
    elif sys.argv[1] == "shutter":
        id = int(sys.argv[2])
        action = int(sys.argv[3])
        shutterAction(id, action)
    elif sys.argv[1] == "gate":
        id = int(sys.argv[2])
        gateAction(id)


if __name__ == '__main__':
    main()
