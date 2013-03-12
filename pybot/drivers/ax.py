
RD_VERSION = 0x00
WRITE_INFO = 0x01
READ_INFO  = 0x02

def getVersion(dev):
    dev.send([RD_VERSION])
    raw = dev.read(3)
    return raw[1] + raw[2] * 256

def write_info(dev, id_motor, regstart, value):
    msg = [WRITE_INFO, id_motor, regstart, value / 256, value % 256]
    print 'msg', msg
    dev.send(msg)
    raw = dev.read(2)
    return raw[1]

def read_info(dev, id_motor, regstart, lenght):
    msg = [READ_INFO, id_motor, regstart, lenght]
    dev.send(msg)
    raw = dev.read(lenght + 1)
    if lenght == 1:
        return raw[1]
    else:
        return raw[1] + raw[2] * 256
   

