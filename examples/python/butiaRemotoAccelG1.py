#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Butia Remoto

import sys
sys.path.append('../../pybot')
import pybot_client
import android
import time

droid = android.Android()

butia = butiaAPI.robot()
modules = butia.getModulesList()
if modules == []:
    print 'No modules detected'
else:
    print modules

s = droid.startSensing()
a = 'q' #no hace nada

time.sleep(1)
while True:
	s = droid.readSensors()
	if s == None:
		print "s == None"
	elif s.error != None:
		print "error"
	else:
		print "roll  y1=" + str(s.result['roll'])
		print "pitch x1=" + str(s.result['pitch'])
		
			
		y1 = s.result['roll']
		x1 = s.result['pitch']
		
		
		if x1 > 45:
			x1 = 45
		elif x1 < -45:
			x1 = -45	
		if y1 > 45:
			y1 = 45
		elif y1 < -45:
			y1 = -45		

		xplusy = x1 + y1
		yminusx = y1 - x1

		#rueda izq la de id mayor
		sentidoIzq = 0 #forward
		if xplusy < 0:
			xplusy = abs(xplusy)
			sentidoIzq = 1

		#rueda der la de id menor
		sentidoDer = 0 #forward
		if yminusx < 0:
			yminusx = abs(yminusx)
			sentidoDer = 1
		xplusy = xplusy*22
		yminusx = yminusx*22

		#normalizo 
		if xplusy > 990:
			xplusy = 990
		if yminusx > 990:
			yminusx = 990
		butia.set2MotorSpeed(str(sentidoDer),str(yminusx), str(sentidoIzq), str(xplusy))			
		
droid.stopSensing()
print "fin"		
						
		
