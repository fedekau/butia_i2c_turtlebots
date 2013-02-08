#! /usr/bin/env python
# -*- coding: utf-8 -*-
# 
# ButiaAPI
# Copyright (c) 2009-2013 Butiá Team butia@fing.edu.uy 
# Butia is a free and open robotic platform
# www.fing.edu.uy/inco/proyectos/butia
# Facultad de Ingeniería - Universidad de la República - Uruguay
#
# Implements abstractions for the comunications with the bobot-server
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

import socket
import string
import math
import threading

ERROR = -1

PYBOT_HOST = 'localhost'
PYBOT_PORT = 2009

class robot:
    

    def __init__(self, host = PYBOT_HOST, port = PYBOT_PORT):
        """
        init the robot class
        """
        self.lock = threading.Lock()
        self.host = host
        self.port = port
        self.client = None
        self.reconnect()
       
    def doCommand(self, msg):
        """
        Executes a command in butia.
        @param msg message to be executed
        """
        msg = msg + '\n'
        ret = ERROR
        self.lock.acquire()
        try:     
            self.client.send(msg) 
            ret = self.client.recv(1024)
            ret = ret[:-1]
        except:
            ret = ERROR
        self.lock.release()
        
        return ret
          
    # connect o reconnect the bobot
    def reconnect(self):
        self.close()
        try:
            self.client = socket.socket()
            self.client.connect((self.host, self.port))  
        except:
            return ERROR
        return 0

    # ask bobot for refresh is state of devices connected
    def refresh(self):
        return self.doCommand('REFRESH')

    # close the comunication with pybot
    def close(self):
        try:
            self.client.close()
            self.client = None
        except:
            return ERROR
        return 0

    #######################################################################
    ### Operations to the principal module
    #######################################################################


    # call the module 'modulename'
    def callModule(self, modulename, board_number, number, function, params = ''):
        if number == '':
            number = 0
        msg = 'CALL ' + modulename + '@' + str(board_number) + ':' + str(number) + ' ' + function
        if params != '':
            msg += ' ' + params
        ret = self.doCommand(msg)
        try:
            ret = int(ret)
        except:
            try:
                ret = float(ret)
            except:
                ret = ERROR
        return ret

    # Close bobot service
    def closeService(self):
        msg = 'QUIT'
        return self.doCommand(msg)

    #######################################################################
    ### Useful functions 
    #######################################################################

    # returns if the module_name is present
    def isPresent(self, module_name):
        module_list = self.get_modules_list()
        return (module_name in module_list)

    # returns a list of modules
    def get_modules_list(self, normal=True):
        msg = 'LIST'
        l = []
        ret = self.doCommand(msg)
        if not (ret == '' or ret == ERROR):
            l = ret.split(',')
        modules = []
        if not(normal):
            for m in l:
                modules.append(self.split_module(m))
        else:
            modules = l

        return modules

    def split_module(self, mbn):
        board = '0'
        number = '0'
        if mbn.count('@') > 0:
            modulename, bn = mbn.split('@')
            board, number = bn.split(':')
        else:
            if mbn.count(':') > 0:
                modulename, number = mbn.split(':')
            else:
                modulename = mbn
        return (number, modulename, board)

    def get_butia_count(self):
        msg = 'BUTIA_COUNT'
        ret = self.doCommand(msg)
        return ret

    # loopBack: send a message to butia and wait to recibe the same
    def loopBack(self, data, board=0):
        msg = 'CALL lback@' + str(board) + ':0 send ' + data
        return self.doCommand(msg)
            
    #######################################################################
    ### Operations for motores.lua driver
    #######################################################################

    def set2MotorSpeed(self, leftSense = 0, leftSpeed = 0, rightSense = 0, rightSpeed = 0, board = 0):
        msg_l = str(leftSense) + ' ' + str(int(leftSpeed / 256.0)) + ' ' + str(leftSpeed % 256)
        msg_r = str(rightSense) + ' ' + str(int(rightSpeed / 256.0)) + ' ' + str(rightSpeed % 256)
        return self.callModule('motors', board, 0, 'setvel2mtr', msg_l + ' ' + msg_r)
     
    def setMotorSpeed(self, idMotor = 0, sense = 0, speed = 0, board = 0):
        msg = str(idMotor) + ' ' + str(sense) + ' ' + str(int(speed / 256.0)) + ' ' + str(speed % 256)
        return self.callModule('motors', board, 0, 'setvelmtr', msg)

    """#######################################################################
    ### Operations for ax.lua driver
    #######################################################################

    def wheel_mode(self, idMotor = '0'):
        msg = idMotor
        return self.callModule('ax', 'wheel_mode', msg)
     
    def joint_mode(self, idMotor = '0', min = '0', max = '1023'):
        msg = idMotor + ' ' + min + ' ' + max
        return self.callModule('ax', 'joint_mode', msg)

	def set_speed(self, idMotor = '0', speed = '0'):
		msg = idMotor + ' ' + speed 
        return self.callModule('ax', 'set_speed', msg)

    def set_position(self, idMotor = '0', pos = '0'):
        msg = idMotor + ' ' + pos
        return self.callModule('ax', 'set_position', msg)

    def get_position(self, idMotor = '0'):
        msg = idMotor
        return self.callModule('ax', 'get_position', msg)

    def ping(self, board=0):
        return self.callModule('placa', board, 0, 'ping')"""
    
    ############################### General calls ###############################
     
    def getBatteryCharge(self, board=0):
        return self.callModule('butia', board, 0, 'get_volt')

    def getVersion(self, board=0):
        return self.callModule('butia', board, 0, 'read_ver')

    def getFirmwareVersion(self, board=0):
        return self.callModule('admin', board, 0, 'getVersion')

    ############################### Sensors calls ###############################

    def getButton(self, number, board=0):
        res = self.callModule('button', board, number, 'getValue')
        if res != ERROR:
            return (1 - res)
        else:
            return res
    
    def getAmbientLight(self, number, board=0):
        m = 65535
        res = self.callModule('light', board, number, 'getValue')
        if res != ERROR:
            return (m - res)
        else:
            return res

    def getDistance(self, number, board=0):
        return self.callModule('distanc', board, number, 'getValue')

    def getGrayScale(self, number, board=0):
        return self.callModule('grey', board, number, 'getValue')

    def getTemperature(self, number, board=0):
        return self.callModule('temp', board, number, 'getValue')

    def getResistance(self, number, board=0):
        vcc = 65535
        raw = self.callModule('res', board, number, 'getValue')
        if not(raw == ERROR):
            return raw * 6800 / (vcc - raw)
        return raw

    def getVoltage(self, number, board=0):
        vcc = 65535
        raw = self.callModule('volt', board, number, 'getValue')
        if not(raw == ERROR):
            return raw * 5 / vcc
        return raw

    def setLed(self, on_off, number, board):
        return self.callModule('led', board, number, 'turn', str(on_off))

    ################################## Extras ##################################

    def modeHack(self, pin, mode, board = 0):
        msg = str(pin) + ' ' + str(mode)
        return self.callModule('hackp', board, 0, 'setMode', msg)

    def setHack(self, pin, value, board = 0):
        msg = str(pin) + ' ' + str(value)
        return self.callModule('hackp', board, 0, 'write', msg)

    def getHack(self, pin, board = 0):
        return self.callModule('hackp', board, 0, 'read', str(pin))

