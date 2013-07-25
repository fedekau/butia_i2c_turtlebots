#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Test General

import sys
sys.path.append('../../pybot')
import pybot_client
import time

butia = pybot_client.robot()

print 'Loaded modules'
print butia.getModulesList()

print 'Butia battery charge'
print butia.getBatteryCharge()

print 'Butia firmware version'
print butia.getFirmwareVersion()

ret = butia.loopBack("hola")
print 'I send: hola'
print 'and get: ' + str(ret)

# BOTH MOTORS

print 'Check both motors'
print 'Check: 0 500 0 500'
ret = butia.set2MotorSpeed(0, 1000, 0, 500)
time.sleep(2)

print 'Stop'
ret = butia.set2MotorSpeed(0, 0, 0, 0)
time.sleep(1)

# LEFT MOTOR

print 'Check left motor'
print 'Check: 0 0 1023'
ret = butia.setMotorSpeed(0, 0, 1023)
time.sleep(1)

print 'Check: 0 1 1023'
ret = butia.setMotorSpeed(0, 1, 1023)
time.sleep(1)

print 'Stop left motor'
ret = butia.setMotorSpeed(0, 0, 0)
time.sleep(1)

# RIGHT MOTOR

print 'Check right motor'
print 'Check: 1 0 1023'
ret = butia.setMotorSpeed(1, 0, 1023)
time.sleep(1)

print 'Check: 1 1 1023'
ret = butia.setMotorSpeed(1, 1, 1023)
time.sleep(1)

print 'Stop left motor'
ret = butia.setMotorSpeed(1, 0, 0)
time.sleep(1)


print 'the end'
butia.close()


