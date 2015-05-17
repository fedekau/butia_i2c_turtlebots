#! /usr/bin/env python
# -*- coding: utf-8 -*-

from pybot import pybot_client
from library import patternsAPI

butia = pybot_client.robot()

negro = 39000
blanco = 22000
idIzq = "1"
idDer = "3"
distMinMark = 200

def main():
    det = patternsAPI.detection()
    salida = det.arMultiGetIdsMarker()
    print salida

    modulos = butia.getModulesList()
    print modulos


    while True:
        butia.set2MotorSpeed("0","600", "0", "600")
        print "pase"
        print str(idIzq) + " "  + str(butia.getGray(idIzq))
        print str(idDer) + " "  + str(butia.getGray(idDer))
        # chequeo a la izquierda
        if butia.getGray(idIzq) < negro and butia.getGray(idDer) >negro:
            busco_camino_izquierda()
            print "corrijo izq"

        #chequeo a la derecha
        if butia.getGray(idIzq)>negro and butia.getGray(idDer)< negro:
            corregir_derecha()
            print "corrijo derecha"

        #si los dos estan en blanco miro a ver si hay senial
        if butia.getGray(idIzq) < negro and butia.getGray(idDer) < negro:
            if det.getMarkerTrigDist("Right") > -1 and det.getMarkerTrigDist("Right") < distMinMark:
                print "encontre la signal Right"
                # busco el camino a la derecha
                busco_camino_derecha()
            else:
                if  det.getMarkerTrigDist("Left") > -1 and det.getMarkerTrigDist("Left") < distMinMark:
                    print "encontre la signal Left"
                    busco_camino_izquierda()
                else:
                    butia.set2MotorSpeed("0","0", "0", "0")
                    print "no vio signal"
                    break


def corregir_izquierda():
    # busco linea a la derecha
    butia.set2MotorSpeed("0","0", "0", "0")
    while butia.getGray(idIzq) == blanco:
          butia.set2MotorSpeed("1", "100", "0", "100") #giro hacia la derecha

def corregir_derecha():
    # busco linea a la izquierda
    butia.set2MotorSpeed("0","0", "0", "0")
    while butia.getGray(idDer) == blanco:
          butia.set2MotorSpeed("0", "100", "1", "100") #giro hacia la izquierda

def busco_camino_izquierda():
    # giro a la izquierda hasta que el sensor derecho este en negro
    while butia.getGray(idDer) != negro:
          butia.set2MotorSpeed("0", "100", "1", "100") #giro hacia la izquierda

def busco_camino_derecha():
        while butia.getGray(idIzq) != negro:
          butia.set2MotorSpeed("1", "100", "0", "100") #giro hacia la derecha

if __name__ == "__main__":
    main()
