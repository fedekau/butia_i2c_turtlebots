
RD_VERSION = 0x00
SEND_DATA = 0x01

def getVersion(dev):
    dev.send([RD_VERSION])
    raw = dev.read(3)
    return raw[1] + raw[2] * 256

def send(dev, data):
    msg = [SEND_DATA] + dev.ordinal(data)
    dev.send(msg)
    raw = dev.read(len(data))
    ret = ''
    for r in raw[1:]:
        if not(r == 0):
            ret = ret + chr(r)
    return ret

