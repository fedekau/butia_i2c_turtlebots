
RD_VERSION = 0x00
SEND_DATA = 0x01

def getVersion(dev):
    dev.send([RD_VERSION])
    raw = dev.read(3)
    return raw[1] + raw[2] * 256

def send(dev, data):
    msg = [GET_VALUE, data]
    dev.send(msg)
    raw = dev.read(len(data))
    return raw[1:]

