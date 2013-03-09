
RESET = 0xFF
GET_FIRMWARE_VERSION = 0xFE

def getVersion(dev):
    dev.send([GET_FIRMWARE_VERSION])
    raw = dev.read(2)
    return raw[1]

def reset(dev):
    dev.send([RESET])

