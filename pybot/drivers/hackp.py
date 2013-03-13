
RD_VERSION = 0x00
SET_MODE = 0x01
READ = 0x02
WRITE = 0x03
WRITE_PORT = 0x04
PORT_IN = 0x05
PORT_OUT = 0x06

def getVersion(dev):
    dev.send([RD_VERSION])
    raw = dev.read(3)
    return raw[1] + raw[2] * 256

def setMode(dev, pin, value):
    msg = [SET_MODE, pin, value]
    dev.send(msg)
    raw = dev.read(2)
    return raw[1]

def read(dev, pin):
    msg = [READ, pin]
    dev.send(pin)
    raw = dev.read(2)
    return raw[1]

def write(dev, pin, value):
    msg = [WRITE, pin, value]
    dev.send(pin)
    raw = dev.read(1)
    return raw[1]

