#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Controlar Pinza
#la pinza izq se mueve entre 1023(abierto) y 74(cerrado)
#la pinza der se mueve entre 0(abierto) y 879(cerrado)

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

PINZA_IZQ = "21"
PINZA_DER = "20"

butia.jointMode(PINZA_IZQ, "0", "1023") #1023 is 300 degrees
butia.jointMode(PINZA_DER, "0", "1023") #1023 is 300 degrees

print "start..."

vel = raw_input("tiempo espera formato 0.05 > ")
inc = int(raw_input("pase el incremento 10 > "))

openDer = 0
closeDer = 879

openIzq = 980
closeIzq = 74

posDer = openDer
posIzq = openIzq
posActDer = openDer
posActIzq = openIzq

#inicio abierto
butia.setPosition(PINZA_DER, str(posDer))
butia.setPosition(PINZA_IZQ, str(posIzq))
time.sleep(1)

while posActDer < closeDer or  posActIzq > closeIzq:
	posDer += inc
	posIzq += -inc
	butia.setPosition(PINZA_DER, str(posDer))
	butia.setPosition(PINZA_IZQ, str(posIzq))

	time.sleep(float(vel))

	if abs(posActDer-butia.getPosition(PINZA_DER)) < 5:
		butia.setPosition(PINZA_DER, str(posActDer-500))

	posActDer = butia.getPosition(PINZA_DER)
	posActIzq = butia.getPosition(PINZA_IZQ)

	#print "posActDer= ", posActDer
	  
butia.close()

