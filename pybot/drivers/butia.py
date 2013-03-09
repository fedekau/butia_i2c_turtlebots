
RD_VERSION = 0x02
GET_VOLT = 0x03

def getVersion(dev):
    dev.send([RD_VERSION])
    raw = dev.read(3)
    return raw[1] + raw[2] * 256

def get_volt(dev):
    dev.send([GET_VOLT])
    raw = dev.read(2)
    return raw[1]

