#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Rutinas para seguidor de lineas junto con el plugin de marcas
al correr levanta dos hilos uno para el manejo del butia (ClaseMain) y otra para el teclado (ClaseTecla)
- para salir presionar c + enter
- para ver los valores de los sensores de grises, G +enter, luego 1 para ver el derecho o
2 para el izquierdo, para salir S+enter, para ver el otro poner nuevamente G y el numero correspondiente.
- Para que comienze a hacer caminar el Robot m + enter, se sale con S y enter


"""

#from pybot import pybot_client

import sys
import os.path
import time

if os.path.exists('/home/olpc/Activities/TurtleBots.activity/plugins/butia/pybot/usb4butia.py'):
    sys.path.append("/home/olpc/Activities/TurtleBots.activity/plugins/butia")



if os.path.exists("/home/olpc/Activities/TurtleBots.activity/plugins/pattern_detection/library/patternsAPI.py"):
    sys.path.append("/home/olpc/Activities/TurtleBots.activity/plugins/pattern_detection")
    from library import patternsAPI
elif os.path.exists("/home/olpc/Activities/TurtleBots.activity/plugins/pattern_detection/library/multiPatternDetectionAPI.py"): #para V19  y anteriores :S
    sys.path.append("/home/olpc/Activities/TurtleBots.activity/plugins/pattern_detection/library")
    import multiPatternDetectionAPI as patternsAPI
else:
    from library import patternsAPI


from pybot import usb4butia
#from pybot import pybot_client
import threading



class ClaseMain():

    def __init__(self):
        print "Inicio ClaseMain"
        #self.detect = patternsAPI.detection()
        #self.detect.init()
        #self.data = data
        #self.butia = pybot_client.robot()
        self.butia = usb4butia.USB4Butia()
        self.idIzq = "2"
        self.idDer = "4"
        self.negroDer = 30000
        self.negroIzq = 40000
        #self.distMinimalSignal = 500
        #self.distSignalLeft = 500
        #print str(self.detect.arMultiGetIdsMarker().split(";"))
        #print str(self.butia.getModulesList())
        #self.detect.isMarkerPresent("Right")


    def run(self):
        self.mover()
        #self.detect.cleanup()
        print "FIN ClaseMain"


    def mover(self):
        while True:
            #self.butia.set2MotorSpeed("0","400", "0", "400")
            time.sleep(0.1)
            if self.butia.getGray(self.idDer) > self.negroDer: #si derecha negro
                self.corregir_derecha()
                print "corrijo izq"
            elif self.butia.getGray(self.idIzq) > self.negroIzq: # si izquierda negro
                self.corregir_izquierda()
                print "corrijo der"

    def corregir_izquierda(self):
        # busco linea a la derecha
        salir = False
        #self.butia.set2MotorSpeed("0","0", "0", "0")
        print "sensor der: " + self.idDer + " valor " + str(self.butia.getGray(self.idDer))
        while self.butia.getGray(self.idDer)< self.negroDer:
            print "sensor der: " + self.idDer + " valor " + str(self.butia.getGray(self.idDer))
            self.butia.set2MotorSpeed("0", "300", "1", "300") #giro hacia la derecha
            time.sleep(0.1)
        self.butia.set2MotorSpeed("0","0", "0", "0")

    def corregir_derecha(self):
        # busco linea a la izquierda
        #self.butia.set2MotorSpeed("0","0", "0", "0")
        salir = False
        print "sensor der: " + self.idIzq + " valor " + str(self.butia.getGray(self.idIzq))
        while self.butia.getGray(self.idIzq) < self.negroIzq :
            print "sensor der: " + self.idIzq + " valor " + str(self.butia.getGray(self.idIzq))
            self.butia.set2MotorSpeed("1", "300", "0", "300") #giro hacia la izquierda
            time.sleep(0.1)
        self.butia.set2MotorSpeed("0","0", "0", "0")




print "Soy el hilo principal"

l = ClaseMain()
l.run()
print "FIN"