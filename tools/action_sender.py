from serial import Serial


def send(blind_id, command):
    if not ((0 <= blind_id <= 8) and (0 <= command <= 2)):
        return -1

    result = (command << 4) | blind_id
    b = bytes([result])

    ser = Serial("/dev/serial0", 115200, timeout=2)

    ser.write(b)
