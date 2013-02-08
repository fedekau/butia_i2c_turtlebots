import butiaAPI
import time

butiabot = butiaAPI.robot()

print 'Loaded modules'
print butiabot.get_modules_list()

print 'Butia battery charge'
print butiabot.getBatteryCharge()

print 'Butia version'
print butiabot.getVersion()

print 'Butia firmware version'
print butiabot.getFirmwareVersion()

ret = butiabot.loopBack("hola")
print 'I send: hola'
print 'and get: ' + ret

# BOTH MOTORS

print 'Check both motors'
print 'Check: 0 500 0 500'
ret = butiabot.set2MotorSpeed(0, 1000, 0, 500)
time.sleep(2)

print 'Stop'
ret = butiabot.set2MotorSpeed(0, 0, 0, 0)
time.sleep(1)

# LEFT MOTOR

print 'Check left motor'
print 'Check: 0 0 1023'
ret = butiabot.setMotorSpeed(0, 0, 1023)
time.sleep(1)

print 'Check: 0 1 1023'
ret = butiabot.setMotorSpeed(0, 1, 1023)
time.sleep(1)

print 'Stop left motor'
ret = butiabot.setMotorSpeed(0, 0, 0)
time.sleep(1)

# RIGHT MOTOR

print 'Check right motor'
print 'Check: 1 0 1023'
ret = butiabot.setMotorSpeed(1, 0, 1023)
time.sleep(1)

print 'Check: 1 1 1023'
ret = butiabot.setMotorSpeed(1, 1, 1023)
time.sleep(1)

print 'Stop left motor'
ret = butiabot.setMotorSpeed(1, 0, 0)
time.sleep(1)


print 'the end'

butiabot.close()


