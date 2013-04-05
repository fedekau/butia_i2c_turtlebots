
RD_VERSION = 0x00
WRITE_INFO = 0x01
READ_INFO  = 0x02

def getVersion(dev):
    dev.send([RD_VERSION])
    raw = dev.read(3)
    return raw[1] + raw[2] * 256

def writeInfo(dev, motor_id, regstart, value):
    msg = [WRITE_INFO, motor_id, regstart, value / 256, value % 256]
    dev.send(msg)
    raw = dev.read(2)
    return raw[1]

def readInfo(dev, motor_id, regstart, lenght):
    msg = [READ_INFO, motor_id, regstart, lenght]
    dev.send(msg)
    raw = dev.read(lenght + 1)
    if lenght == 1:
        return raw[1]
    else:
        return raw[1] + raw[2] * 256

def wheelMode(dev, motor_id):
    msg = [WRITE_INFO, motor_id, 0x06, 0x00, 0x00]
    dev.send(msg)
    raw = dev.read(1)
    msg = [WRITE_INFO, motor_id, 0x08, 0x00, 0x00]
    dev.send(msg)
    raw = dev.read(1)
    return raw[1]

def jointMode(dev, motor_id, _min, _max):
    msg = [WRITE_INFO, motor_id, 0x06, _min / 256, _min % 256]
    dev.send(msg)
    raw = dev.read(1)
    msg = [WRITE_INFO, motor_id, 0x08, _max / 256, _max % 256]
    dev.send(msg)
    raw = dev.read(1)

def setPosition(dev, motor_id, pos):
    msg = [WRITE_INFO, motor_id, 0x1E, pos / 256, pos % 256]
    dev.send(msg)
    raw = dev.read(1)

def getPosition(dev, motor_id):
    msg = [READ_INFO, motor_id, 0x24, 2]
    dev.send(msg)
    raw = dev.read(3)
    raw_angle = raw[2] * 256 + raw[3]
    return raw_angle * 0.29

def setSpeed(dev, motor_id, speed):
    vel = speed * 1.496
    msg = [motor_id, 0x20, speed / 256, speed % 256]
    dev.send(msg)
    raw = dev.read(1)

