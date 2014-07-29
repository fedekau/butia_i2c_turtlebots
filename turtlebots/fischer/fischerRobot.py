#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Fischer abstraction
#
# Copyright (c) 2014 Andrés Aguirre <aaguirre@fing.edu.uy>
# Copyright (c) 2014 Mercedes Marzoa <mmarzoa@fing.edu.uy>
# Copyright (C) 2014 Alan Aguiar <alanjas@hotmail.com>
# Copyright (c) 2014 Butiá Team butia@fing.edu.uy 
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
import threading
from time import sleep, time

ACTUADOR_M1  =  1 
ACTUADOR_M2  =  2
ACTUADOR_MB  =  3

BAS_MSG = [0xa5, 0x01, 0x8d]
MID_MSG = [0x0f, 0x00, 0x00, 0x00, 0x00]
END_MSG = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]

ACT_1_MSG = BAS_MSG + [0x01, 0x3f, 0x00, 0x00] + MID_MSG * 4 + END_MSG
ACT_2_MSG = BAS_MSG + [0x04, 0xc0, 0x0f, 0x00] + MID_MSG * 4 + END_MSG
ACT_B_MSG = BAS_MSG + [0x05, 0xff, 0x0f, 0x00] + MID_MSG * 4 + END_MSG


class FischerRobot():

    def __init__(self, dev, debug=False):
        self.dev = dev
        self.debug = debug
        self.sensors = [0, 0, 0]
        self.actuators = [0, 0]
        self.pollSensor = [time(),time(),time()]
        self.both = False
        self.msg_to_send = []
        self.lock = threading.Lock()
        self.threadOff = True                       

    def _debug(self, message, err=''):
        if self.debug:
            print message, err

    def open_ft(self):
        """
        Open the comunication
        """
        self.dev.open_device()

    def close_ft(self):
        """
        Close the comunication
        """
        self.dev.close_device()

    def get_info(self):
        """
        Get Fischer info: manufacture..
        """
        return self.dev.get_info()

    def getSensor(self, idSensor):
        now = time()
        if self.pollSensor[idSensor]+0.50 < now:
            ret = self.dev.read(98)
            ret = self.dev.read(98)
            self._conectSensor(ret)              
            self.pollSensor[idSensor] = now
        return self.sensors[idSensor]

    def turnActuator(self, idActuator, powerOn):
        if  self.threadOff:
            t = threading.Thread(target=self._sendMsg)
            t.start()
            self.threadOff = False
        idActuator = idActuator - 1
        if powerOn == 1:
            if self.both == False: 
                self.actuators[idActuator] = 1
                if ((idActuator != ACTUADOR_M1-1 and self.actuators[ACTUADOR_M1-1] == 1) 
                    or (idActuator != ACTUADOR_M2-1 and self.actuators[ACTUADOR_M2-1] == 1)):
                    self.both = True
                    msg = self._createActuatorMsg(ACTUADOR_MB)
                else:
                    msg = self._createActuatorMsg(idActuator+1)            
                self._actuatorOn(msg, idActuator)      
        else:
            self._actuatorOff(idActuator)

    def quit(self):      
        self.threadOff = True

    def _actuatorOn(self, msg, idActuator):
        if self.both == True:
            if idActuator == ACTUADOR_M1-1: 
                msgAux = self._createActuatorMsg(ACTUADOR_M2)
            else:
                msgAux = self._createActuatorMsg(ACTUADOR_M1)              
            msgAux[3] = 0x00
            self.lock.acquire()
            self.msg_to_send = msgAux 
            self.lock.release()	
        self.lock.acquire()
        self.msg_to_send = msg
        self.lock.release()

    def _actuatorOff(self, idActuator):    
        if self.actuators[idActuator] == 1:
            self.actuators[idActuator] = 0       
            if self.both:
                msg = self._createActuatorMsg( ACTUADOR_MB)        
                msg[3]=0x00
                self.lock.acquire()
                self.msg_to_send = msg
                self.lock.release()	
                self.both = False
                if  idActuator != ACTUADOR_M1-1: 
                    idActuator = ACTUADOR_M1
                else:
                    idActuator = ACTUADOR_M2                
                msg = self._createActuatorMsg(idActuator)
                self._actuatorOn(msg, idActuator-1)
            else:                
                msg = self._createActuatorMsg(idActuator+1)            
                msg[3]=0x00
                self.lock.acquire()
                self.msg_to_send = msg
                self.lock.release()
            
    def _createActuatorMsg(self, num):
        if num == ACTUADOR_M1:
            return ACT_1_MSG[:]
        elif num == ACTUADOR_M2:
            return ACT_2_MSG[:]
        else:
            return ACT_B_MSG[:]
        #Si reversa llamar a __modifyReverse
        #Si cambia de potencia llamar a _modifyPower

    def _sendMsg(self):
        while self.threadOff == False:
            self.dev.write(self.msg_to_send)

    def _modifyReverse(self, num, msg, onPower):
        if onPower == ACTUADOR_MB:
            if num == ACTUADOR_M1:
                msg[4] = 0x06
            elif num == ACTUADOR_M2:
                msg[4] = 0x09
            elif num == ACTUADOR_MB:
                msg[4] = 0x0a
        else:
            if num == ACTUADOR_M1:
                msg[4] = 0x02
            elif num == ACTUADOR_M2:
                msg[4] = 0x08
        return msg

    def _modifyPower(self, num, msg, onPower, power):
        if power == 40 or power == 70:
            power = power - 10

        if onPower == ACTUADOR_M1:
            power = self._calculatePower(11, power)
        elif onPower == ACTUADOR_M2:
            power = self._calculatePower(100, power)
            msg[5] = self._byteFive(power)
        else:
            power = self._calculatePower(11, power) + self._calculatePower(100, power)
            msg[5] = self._byteFive(power)

        msg[4]=hex(int(str(power),8))                      
        return msg

    def _byteFive(self, power):
        if power == 10 or power == 60 or power == 70:
            b = 0x00
        elif power == 20:
            b = 0x02
        elif power == 30 or power == 40:
            b = 0x04
        elif power == 50:
            b = 0x06
        elif power == 80:
            b = 0x0b
        elif power == 90:
            b = 0x0d
        else:
            b = 0x0f 
        return b

    def _calculatePower(self, x, power):
        if power >= 0 and power <= 30:
            power = x*((power-10)/10)                
        elif power >= 50 and power <= 60:
            power = x*(power-20)/10
        else:
            power = x*(power-30)/10
        return power

    def _conectSensor(self, msg):
        self.sensors[0] = 0
        self.sensors[1] = 0
        self.sensors[2] = 0
        if msg[3]==2 and msg[11]==83:#I2
            self.sensors[1] = 1 
        elif msg[3]==1 and msg[11]==92:#I1
            self.sensors[0] = 1
        elif msg[3]==4 and msg[11]==79:#I3
            self.sensors[2] = 1
        elif msg[3]==3 and msg[11]==80:#I1 e I2
            self.sensors[0] = 1
            self.sensors[1] = 1
        elif msg[3]==6 and msg[11]==67:#I2 e I3
            self.sensors[1] = 1
            self.sensors[2] = 1
        elif msg[3]==5 and msg[11]==76:#I1 e I3
            self.sensors[0] = 1
            self.sensors[2] = 1
        elif msg[3]==7 and msg[11]==64:#all
            self.sensors[0] = 1
            self.sensors[1] = 1
            self.sensors[2] = 1

