import socket
import sys

from asylum import config
from asylum.asylumd import jsonrpc


socket_loc = config['ASYLUMD']['socket_loc']


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


def writeMemory(type, id, data):
    if type < 0 or type > 1 or id < 0 or id > 9:
        return
    if data < 0 or data > 0xFFFFFFFF:
        return

    hex_data = str.format('{:08X}', data)

    req = jsonrpc.JsonRpcRequest(
        method="writeMemory",
        params=[type, id, hex_data])
    sendToServer(req)


def readMemory(type, id):
    if type < 0 or type > 1 or id < 0 or id > 9:
        return

    req = jsonrpc.JsonRpcRequest(
        method="readMemory",
        params=[type, id],
        id=0)
    resp = sendToServer(req).result
    if resp[0:2] == 'ok':
        print(resp[3:])
    else:
        print(resp)


def main():
    if len(sys.argv) < 2:
            print("asylum_client.py ping")
            print("asylum_client.py shutter [id] [action]")
            print("asylum_client.py gate [id]")
            print("asylum_client.py readmem [type] [id]")
            print("asylum_client.py writemem [type] [id] [data]")
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
    elif sys.argv[1] == 'readmem':
        type = int(sys.argv[2])
        id = int(sys.argv[3])
        readMemory(type, id)
    elif sys.argv[1] == 'writemem':
        type = int(sys.argv[2])
        id = int(sys.argv[3])
        data = int(sys.argv[4], 0)
        writeMemory(type, id, data)


if __name__ == '__main__':
    main()
