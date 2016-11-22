#i2c
RD_VERSION = 0x00

OPEN_I2C = 0x05
START_I2C = 0x06
IDLE_I2C = 0x07
WRITE_I2C = 0x08
READ_I2C = 0x09
STOP_I2C = 0x10
CLOSE_I2C = 0x11
RESTART_I2C = 0x12
ACK_I2C = 0x13
NOT_ACK_I2C = 0x14
DATA_READY_I2C = 0x15

ERROR = -1


def getVersion(dev):

    dev.send([RD_VERSION])
    raw = dev.read(3)
    return raw[1] + raw[2] * 256


def openI2C(dev):

	msg=[OPEN_I2C]
	dev.send(msg)
	raw = dev.read(1)
	return raw


def startI2C(dev):

	msg=[START_I2C]
	dev.send(msg)
	raw = dev.read(1)
	return raw


def stopI2C(dev):

	msg=[STOP_I2C]
	dev.send(msg)
	raw = dev.read(1)
	return raw


def restartI2C(dev):

	msg=[RESTART_I2C]
	dev.send(msg)
	raw = dev.read(1)
	return raw


def writeI2C(dev, to_send):

	msg=[WRITE_I2C, to_send]
	dev.send(msg)
	raw = dev.read(1)
	return raw

def readI2C(dev):
	msg=[READ_I2C]
	dev.send(msg)
	raw = dev.read(2)
	return raw[1]


def ackI2C(dev):

	msg=[ACK_I2C]
	dev.send(msg)
	raw = dev.read(2)
	return raw


def notAckI2C(dev):

	msg=[NOT_ACK_I2C]
	dev.send(msg)
	raw = dev.read(2)
	return raw


def idleI2C(dev):

	msg=[IDLE_I2C]
	dev.send(msg)
	raw = dev.read(2)
	return raw


def closeI2C(dev):

	msg=[CLOSE_I2C]	
	dev.send(msg)
	raw = dev.read(2)
	return raw


def dataReadyI2C(dev):

	msg=[DATA_READY_I2C]
	dev.send(msg)
	raw = dev.read(1)
	return raw

def putcI2C(dev, to_send):

	msg=[PUT_I2C, to_send]
	dev.send(msg)
	raw = dev.read(2)
	return raw


def getcI2C(dev):

	msg=[GET_I2C]
	dev.send(msg)
	raw = dev.read(2)
	return raw
