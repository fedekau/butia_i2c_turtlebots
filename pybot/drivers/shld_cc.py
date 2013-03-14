
RD_VERSION = 0x00
SET_VEL_2MTR = 0x01
SET_VEL_MTR = 0x02

def getVersion(dev):
    dev.send([RD_VERSION])
    raw = dev.read(3)
    return raw[1] + raw[2] * 256

def setvel2mtr(dev, sentido1, on1, sentido2, on2):
    msg = [SET_VEL_2MTR, sentido1, on1, sentido2, on2]
    dev.send(msg)
    raw = dev.read(1)
    return raw[0]

