#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Luchador Sumo

import sys
sys.path.append('../../pybot')
import pybot_client
import time
import random

#definicion de constantes
VAL_LIMITE = 25000 #valor limite para diferenciar entre un negro y un blanco
VENTANA = 10 #cuanto tiene que contar antes de girar hacia el otro lado
INCSPEED = 20 #cuanto tiene que contar antes de aumentar la velocidad

#variables
contVent = 0
aumentVel = 0

butia = pybot_client.robot()
modulos = butia.getModulesList()
print modulos

while True:
	sen1 = butia.getGray(4) #leo el valor del sensor
	print sen1
	if sen1 == -1:
		sen1 = "400"
				
	if int(sen1) >= VAL_LIMITE:
		aumentVel = aumentVel + 1
		print aumentVel
		if aumentVel <= INCSPEED:		
			print "avanzo vel 300"
			butia.set2MotorSpeed("0","300", "0", "300")
		else:
			print "avanzo vel 600"
			butia.set2MotorSpeed("0","600", "0", "600")
	else:
		butia.set2MotorSpeed("0", "0", "0", "0") #giro hacia la derecha por el doble del tiempo
		time.sleep(0.5)
		butia.set2MotorSpeed("1", "400", "1", "400") #giro hacia la derecha por el doble del tiempo
		time.sleep(2)
		vel = random.randint(200, 1020)
		butia.set2MotorSpeed("0", str(vel), "1", str(vel)) #giro hacia la derecha por el doble del tiempo
		time.sleep(random.randint(1, 4))
			
		
