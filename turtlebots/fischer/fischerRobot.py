#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Fischer abstraction
#
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

ACTUADOR_M1  =  1 
ACTUADOR_M2  =  2
ACTUADORES = [ACTUADOR_M1, ACTUADOR_M2]
ON    =  1
OFF   =  0
sensors = [OFF, OFF, OFF]

#act1 + act2 = act ambos
#byte 4
#0x01 + 0x04 = 0x05
#byte 5
#0x3f + 0xc0 = 0xff

BAS_MSG = [0xa5, 0x01, 0x8d]
MID_MSG = [0x0f, 0x00, 0x00, 0x00, 0x00]
END_MSG = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]

ACT_1_MSG = BAS_MSG + [0x01, 0x3f, 0x00, 0x00] + MID_MSG * 4 + END_MSG
ACT_2_MSG = BAS_MSG + [0x04, 0xc0, 0x0f, 0x00] + MID_MSG * 4 + END_MSG
ACT_B_MSG = BAS_MSG + [0x05, 0xff, 0x0f, 0x00] + MID_MSG * 4 + END_MSG

def createActuatorMsg(num):
    if num == ACTUADOR_M1:
        return ACT_1_MSG
    elif num == ACTUADOR_M2:
        return ACT_2_MSG
    else:
        return ACT_B_MSG

def conectSensor(msg):
    sensors[0] = 0
    sensors[1] = 0
    sensors[2] = 0
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


class FischerRobot():

    def __init__(self, dev, debug=False):
        self.dev = dev
        self.debug = debug

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
        ret = self.dev.read(98)
        conectSensor(ret)
        return sensors[idSensor]

    def turnActuator(self, idActuator):
        msg = createActuatorMsg(idActuator)
        self.dev.write(msg)

