#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Butia Remoto

import sys
sys.path.append('../../pybot')
import pybot_client
import time

butia = pybot_client.robot()
modules = butia.getModulesList()
if modules == []:
    print 'No modules detected'
else:
    print modules

MOTOR_1 = "1"
MOTOR_2 = "2"

butia.jointMode(MOTOR_1, "0", "1023") #1023 is 300 degrees
butia.jointMode(MOTOR_2, "0", "1023") #1023 is 300 degrees

error = False
while not error:
    butia.setPosition(MOTOR_1,"0")
    butia.setPosition(MOTOR_2,"0")
    time.sleep(2)
    print "motors set to 0 position and the position of the motors is", butia.getPosition(MOTOR_1), butia.getPosition(MOTOR_2)
    butia.setPosition(MOTOR_1,"300")
    butia.setPosition(MOTOR_2,"300")
    time.sleep(2)
    print "motors set to 300 position and the position of the motors is", butia.getPosition(MOTOR_1), butia.getPosition(MOTOR_2)
    butia.setPosition(MOTOR_1,"600")
    butia.setPosition(MOTOR_2,"600")
    time.sleep(2)
    print "motors set to 600 position and the position of the motors is", butia.getPosition(MOTOR_1), butia.getPosition(MOTOR_2)
    butia.setPosition(MOTOR_1,"900")
    butia.setPosition(MOTOR_2,"900")
    time.sleep(2)
    print "motors set to 900 position and the position of the motors is", butia.getPosition(MOTOR_1), butia.getPosition(MOTOR_2)
    butia.setPosition(MOTOR_1,"1020")
    butia.setPosition(MOTOR_2,"1020")
    time.sleep(2)
    print "motors set to 1020 position and the position of the motors is", butia.getPosition(MOTOR_1), butia.getPosition(MOTOR_2)

butia.close()

