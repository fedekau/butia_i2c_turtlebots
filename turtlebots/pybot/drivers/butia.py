
RD_VERSION = 0x02
GET_VOLT = 0x03

def getVersion(dev):
    dev.send([RD_VERSION])
    raw = dev.read(3)
    return raw[1] + raw[2] * 256

def getVolt(dev):
    dev.send([GET_VOLT])
    raw = dev.read(2)
    if raw[1] == 255:
        return raw[1]
    else:
        return raw[1] / 10.0

