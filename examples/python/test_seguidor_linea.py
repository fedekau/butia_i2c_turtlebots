#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Seguidor de linea

import sys
sys.path.append('../../pybot')
import pybot_client
import time

#definicion de constantes
VAL_LIMITE = 25000 #valor limite para diferenciar entre un negro y un blanco
VENTANA = 10 #cuanto tiene que contar antes de girar hacia el otro lado
INCSPEED = 30 #cuanto tiene que contar antes de aumentar la velocidad
GIROIZQ = 0
GIRODER = 1
AVANLEN = 2
AVANRAP = 3

#variables inicialization
lastFind = 0 # cero = derecha, uno = izquierda. Esto dice hacia donde estaba girando the last time I found black
aumentVel = 0
encontre = False
cont = 0
factor = 0
estado = 0

#otras
BLANCO = 0
NEGRO = 65536
ERROR = -1

butia = pybot_client.robot()
modules = butia.getModulesList()
if modules == []:
    print 'No modules detected'
else:
    print modules

number = 0
for s in modules:
    if s.startswith('grey:'):
        number = s.strip('grey:')
number = int(number)

print raw_input("Calibrando blanco, enter para continuar ")
val = butia.getGray(number)
if not(val == ERROR):
    BLANCO = val

print raw_input("Calibrando negro, enter para continuar ")
val = butia.getGray(number)
if not(val == ERROR):
    NEGRO = val

VAL_LIMITE = (BLANCO + NEGRO) // 2
print "Blanco: " + str(BLANCO) + " Negro: " + str(NEGRO)
print "Limit value: " + str(VAL_LIMITE)
print raw_input("Enter para continuar...")

while True:
    val = butia.getGray(number) #leo el valor del sensor
    print val
    
    if val == ERROR:
        val = VAL_LIMITE - 10
        
    if not(val == ERROR) and val >= VAL_LIMITE:
        print "avanzando..."
        aumentVel = aumentVel + 1
        print aumentVel
        if aumentVel <= INCSPEED and estado != AVANLEN:        
            print "avanzo vel 800"
            butia.set2MotorSpeed(0, 400, 0, 400)
            estado = AVANLEN
        else:
            if aumentVel > INCSPEED and estado != AVANRAP:        
                print "avanzo vel 800"
                butia.set2MotorSpeed(0, 800, 0, 800)
                estado = AVANRAP
    else:
        aumentVel = 0 #reseteo la variable que controla la velocidad
        encontre = False
        factor = 2
        cont = 0
        while (not encontre):            
            print "searching black line..."
            if lastFind == 0 and estado != GIRODER:
                print "girando derecha"
                butia.set2MotorSpeed(1, 300, 0, 300) #giro hacia la derecha
                estado = GIRODER
            else:
                if lastFind == 1 and estado != GIROIZQ:
                    print "girando izquierda"
                    butia.set2MotorSpeed(0, 300, 1, 300) #giro hacia la izquierda 
                    estado = GIROIZQ
            cont = cont + 1
            if cont > factor*VENTANA:
                lastFind = not lastFind
                cont = 0
                factor = factor*2
            print cont
            val = butia.getGray(number) #leo el valor del sensor
            print val
            if val == ERROR:
                val = VAL_LIMITE - 10        
            if not(val == ERROR) and val >= VAL_LIMITE:
                encontre = True

