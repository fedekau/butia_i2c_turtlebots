#! /usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import os.path

if os.path.exists('/home/olpc/Activities/TurtleBots.activity'):
    sys.path.append("/home/olpc/Activities/TurtleBots.activity/plugins/butia")

if os.path.exists("/home/olpc/Activities/TurtleBots.activity/plugins/pattern_detection/library"):
    sys.path.append("/home/olpc/Activities/TurtleBots.activity/plugins/pattern_detection")

from pybot import usb4butia
from library import patternsAPI



def girar_derecha(butia,idDer,negroDer):
    # giro hacia la izquieda hasta que el grisizquierda este en negro y el
    #gris izquierda en blanco
    #salir = False
    while butia.getGray(idDer) < negroDer:#and self.butia.getGray(self.idIzq)  > self.negroIzq and not salir:
        butia.set2MotorSpeed("1", "400", "0", "400") #giro hacia la izquierda
        print str(butia.getGray(idDer))
    #butia.set2MotorSpeed("0", "0", "0", "0")


detect = patternsAPI.detection()
detect.init()
butia = usb4butia.USB4Butia()
idIzq = "4"
idDer = "2"
negroDer = 29000
negroIzq = 50000
distMinimalSignal = 500
distSignalRow = 500
idBoton = "3"

print "hola"
print butia.getButton(idBoton)

while butia.getButton(idBoton)==0:
    butia.set2MotorSpeed("0","300", "0", "300")
    if detect.isMarkerPresent("Right") and detect.getMarkerTrigDist("Right") < distSignalRow:
        girar_derecha(butia,idIzq,negroDer)

detect.cleanup()
butia.set2MotorSpeed("0", "0", "0", "0")
