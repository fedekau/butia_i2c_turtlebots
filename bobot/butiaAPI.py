#! /usr/bin/env python
# -*- coding: utf-8 -*-
# 
# ButiaAPI
# Copyright (c) 2009, 2010, 2011, 2012 Butiá Team butia@fing.edu.uy 
# Butia is a free open plataform for robotics projects
# www.fing.edu.uy/inco/proyectos/butia
# Facultad de Ingenieria - Universidad de la República - Uruguay
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

ERROR_SENSOR_READ = -1

BUTIA_1 = 20

BOBOT_HOST = 'localhost'
BOBOT_PORT = 2009

class robot:
    

    def __init__(self, host = BOBOT_HOST, port = BOBOT_PORT):
        """
        init the robot class
        """
        self.lock = threading.Lock()
        self.host = host
        self.port = port
        self.client = None
        self.fclient = None
        self.ver = ERROR_SENSOR_READ
        self.reconnect()

       
    def doCommand(self, msg):
        """
        Executes a command in butia.
        @param msg message to be executed
        """
        msg = msg +'\n'
        ret = ERROR_SENSOR_READ
        self.lock.acquire()
        try:     
            self.client.send(msg) 
            ret = self.fclient.readline()
            ret = ret[:-1]
        except:
            ret = ERROR_SENSOR_READ # Doesn't return here to release the lock
        self.lock.release()
        
        if ((ret == 'nil value') or (ret == None) or (ret == 'fail') or (ret == 'missing driver')):
            ret = ERROR_SENSOR_READ
        return ret
          
    # connect o reconnect the bobot
    def reconnect(self):
        self.close()
        try:
            self.client = socket.socket()
            self.client.connect((self.host, self.port))  
            self.fclient = self.client.makefile()
            msg = 'INIT'
            #bobot server instance is running, but we have to check for new or remove hardware
            self.doCommand(msg)
        except:
            return ERROR_SENSOR_READ
        return 0

    # ask bobot for refresh is state of devices connected
    def refresh(self):
        msg = 'REFRESH'
        return self.doCommand(msg)

    # close the comunication with the bobot
    def close(self):
        try:
            if self.fclient != None:
                self.fclient.close()
                self.fclient = None
            if self.client != None:
                self.client.close()
                self.client = None
        except:
            return ERROR_SENSOR_READ
        return 0

    #######################################################################
    ### Operations to the principal module
    #######################################################################


    # call the module 'modulename'
    def callModule(self, modulename, function , params = ''):
        msg = 'CALL ' + modulename + ' ' + function
        if params != '' :
            msg += ' ' + params
        ret = self.doCommand(msg)
        try:
            ret = int(ret)
        except:
            ret = ERROR_SENSOR_READ
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
    def getModulesList(self):
        msg = 'LIST'
        l = []
        ret = self.doCommand(msg)
        if not (ret == '' or ret == ERROR_SENSOR_READ):
            l = ret.split(',')
        return l

    # loopBack: send a message to butia and wait to recibe the same
    def loopBack(self, data):
        msg = 'lback send ' + data
        return = self.doCommand(msg)

    #######################################################################
    ### Operations for motores.lua driver
    #######################################################################

    def set2MotorSpeed(self, leftSense = '0', leftSpeed = '0', rightSense = '0', rightSpeed = '0'):
        msg = leftSense + ' ' + leftSpeed + ' ' + rightSense + ' ' + rightSpeed
        return self.callModule('motors', 'setvel2mtr', msg)
     
    def setMotorSpeed(self, idMotor = '0', sense = '0', speed = '0'):
        msg = idMotor + ' ' + sense + ' ' + speed
        return self.callModule('motors', 'setvelmtr', msg)

    #######################################################################
    ### Operations for ax.lua driver
    #######################################################################

    def wheelMode(self, idMotor = '0'):
        msg = idMotor
        return self.callModule('ax', 'wheelMode', msg)
     
    def jointMode(self, idMotor = '0', min = '0', max = '1023'):
        msg = idMotor + ' ' + min + ' ' + max
        return self.callModule('ax', 'jointMode', msg)

    def setPosition(self, idMotor = '0', pos = '0'):
        msg = idMotor + ' ' + pos
        return self.callModule('ax', 'setPosition', msg)

    def getPosition(self, idMotor = '0'):
        msg = idMotor
        return self.callModule('ax', 'getPosition', msg)

    #######################################################################
    ### Operations for butia.lua driver
    #######################################################################

    def getBatteryCharge(self):
        return self.callModule('butia', 'getVolt')

    def getVersion(self):
        return self.callModule('butia', 'getVersion')

    def getFirmwareVersion(self):
        return self.callModule('admin', 'getVersion')    

    ############################### Sensors calls ###############################
    
    def getButton(self, number=''):
        return self.callModule('button:' + str(number), 'getValue')

    def getLight(self, number=''):
        return self.callModule('light:' + str(number), 'getValue')

    def getDistance(self, number=''):
        return self.callModule('distanc:' + str(number), 'getValue')
    
    def getGray(self, number=''):
        return self.callModule('grey:' + str(number), 'getValue')

    def getTemperature(self, number=''):
        return self.callModule('temp:' + str(number), 'getValue')

    def setLed(self, nivel = 1, number= ''):
        return self.callModule('led:' + self.aux + str(number), 'setLight', str(math.trunc(nivel)))

