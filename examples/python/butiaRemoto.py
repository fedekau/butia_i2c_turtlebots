#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Butia Remoto

import sys
sys.path.append('../../pybot')
import pybot_client

butia = pybot_client.robot()
modules = butia.getModulesList()
if modules == []:
    print 'No modules detected'
else:
    print modules

a = 'z' #no hace nada
vel = 600

while a != 'q':
    a = raw_input("Choose your action f, v, j, k: ")
	
    if a == 'f':
        butia.set2MotorSpeed("0", str(vel), "0", str(vel))	#forward
    elif a == 'v':
        butia.set2MotorSpeed("1",str(vel), "1", str(vel))	#backward
    elif a == 'j':
        butia.set2MotorSpeed("0",str(vel), "1", str(vel))	#left
    elif a == 'k':
        butia.set2MotorSpeed("1",str(vel), "0", str(vel))	#right	
    elif a == '+':
        vel = vel + 50
        if vel > 1023:
            vel = 1023
        print vel
    elif a == '-':
        vel = vel - 50
        if vel < 0:
            vel = 0
        print vel
	else:	
		butia.set2MotorSpeed("0","0", "0", "0")	#stop	

