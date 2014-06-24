#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Andrés Aguirre  aaguirre@fing.edu.uy 
# Copyright (c) 2014 Mercedes Marzoa mmarzoa@fing.edu.uy
# Copyright (c) 2011-2014 Butiá Team butia@fing.edu.uy 
# Butia is a free and open robotic platform
# www.fing.edu.uy/inco/proyectos/butia
# Facultad de Ingeniería - Universidad de la República - Uruguay
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import usb.core
import time
import struct
import thread

FISCHER_LT_DEVICE_NUMBER  = 0x146a
FISCHER_LT_PRODUCT_NUMBER = 0x000a

OUT_ENDPOINT =  0X01
IN_ENDPOINT  =  0X81
ACTUADOR_M1  =  1 
ACTUADOR_M2  =  2
ACTUADORES = [ACTUADOR_M1,ACTUADOR_M2]
ON    =  1
OFF   =  0
SENSOR =  [ON,OFF]
sensors = [SENSOR,SENSOR,SENSOR]
dev = usb.core.find()


def createActuatorMsg(num):
    if num == ACTUADOR_M1:
        msg = [0xa5,  0x01, 0x8d , 0x01 , 0x3f , 0x00 , 0x00 , 0x0f , 0x00 , 0x00 , 0x00 , 0x00 , 0x0f , 0x00 , 0x00 , 0x00 , 0x00 , 0x0f , 0x00 , 0x00 , 0x00 , 0x00 , 0x0f , 0x00 , 0x00 , 0x00 , 0x00 , 0x00 , 0x00 , 0x00 , 0x00 , 0x00 , 0x00 , 0x00 , 0x00] 
        return msg
    elif num == ACTUADOR_M2:
        msg = [0xa5,  0x01, 0x8d , 0x04 , 0xc0 , 0x0f , 0x00 , 0x0f , 0x00 , 0x00 , 0x00 , 0x00 , 0x0f , 0x00 , 0x00 , 0x00 , 0x00 , 0x0f , 0x00 , 0x00 , 0x00 , 0x00 , 0x0f , 0x00 , 0x00 , 0x00 , 0x00 , 0x00 , 0x00 , 0x00 , 0x00 , 0x00 , 0x00 , 0x00 , 0x00] 
        return msg
    else:#ambos
        msg = [0xa5,  0x01, 0x8d , 0x05 , 0xff , 0x0f , 0x00 , 0x0f , 0x00 , 0x00 , 0x00 , 0x00 , 0x0f , 0x00 , 0x00 , 0x00 , 0x00 , 0x0f , 0x00 , 0x00 , 0x00 , 0x00 , 0x0f , 0x00 , 0x00 , 0x00 , 0x00 , 0x00 , 0x00 , 0x00 , 0x00 , 0x00 , 0x00 , 0x00 , 0x00] 
        return msg


def conectSensor(msg):
    sensors[0] = sensors[2] = sensors[1] = 0 
    if msg[3]==2 and msg[11]==83:#I2
        sensors[1] = 1 
    elif msg[3]==1 and msg[11]==92:#I1
        sensors[0] = 1
    elif msg[3]==4 and msg[11]==79:#I3
        sensors[2] = 1
    elif msg[3]==3 and msg[11]==80:#I1 e I2
        sensors[0] = 1
        sensors[1] = 1
    elif msg[3]==6 and msg[11]==67:#I2 e I3
        sensors[1] = 1
        sensors[2] = 1
    elif msg[3]==5 and msg[11]==76:#I1 e I3
        sensors[0] = 1
        sensors[2] = 1
    elif msg[3]==7 and msg[11]==64:#all
        sensors[0] = 1
        sensors[1] = 1
        sensors[2] = 1

def ActuatorOn(msg):
    while True:
        dev.write(OUT_ENDPOINT, msg, 0)

def turnOnActuator(idActuator):    
    msg = createActuatorMsg(idActuator)
    #thread.start_new_thread(ActuatorOn, (msg,))
    dev.write(OUT_ENDPOINT, msg, 0) #crear hilo        

#def turnOffActuator(idActuator):
    #matar hilo

def getValueSensor(idSensor):
    ret = dev.read(IN_ENDPOINT,98, 0) #FIXME change 98 for a constant that represent that number!
    conectSensor(ret)
    return sensors[idSensor]

#def conectController(): #FIXME why this is commented?

# find our device
dev = usb.core.find(idVendor=FISCHER_LT_DEVICE_NUMBER, idProduct=FISCHER_LT_PRODUCT_NUMBER)
# was it found?
if dev is None: 
    raise ValueError('Device not found')
print "Connected"
# set the active configuration.
dev.set_configuration()

#conectController()    
while True:
    #print getValueSensor(0)
    turnOnActuator(1)
    time.sleep(1)

