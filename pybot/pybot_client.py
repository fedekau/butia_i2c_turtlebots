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
import errno
from functions import ButiaFunctions

ERROR = -1

PYBOT_HOST = 'localhost'
PYBOT_PORT = 2009

class robot(ButiaFunctions):
    
    def __init__(self, host = PYBOT_HOST, port = PYBOT_PORT):
        """
        init the robot class
        """
        self.lock = threading.Lock()
        self.host = host
        self.port = port
        self.client = None
        self.reconnect()
       
    def _doCommand(self, msg):
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
        except Exception, e:
            if hasattr(e, 'errno'):
                if e.errno == errno.EPIPE:
                    self.reconnect()
            ret = ERROR
        self.lock.release()
        
        return ret

    def reconnect(self):
        """
        connect o reconnect the bobot
        """
        self.close()
        try:
            self.client = socket.socket()
            self.client.connect((self.host, self.port))  
        except:
            return ERROR
        return 0

    def refresh(self):
        """
        ask bobot for refresh is state of devices connected
        """
        self._doCommand('REFRESH')

    def close(self):
        """
        close the comunication with pybot
        """
        try:
            self.client.close()
            self.client = None
        except:
            return ERROR
        return 0

    def callModule(self, modulename, board_number, number, function, params = []):
        """
        call the module 'modulename'
        """
        msg = 'CALL ' + modulename + '@' + str(board_number) + ':' + str(number) + ' ' + function
        if not(params == []):
            msg = msg + ' ' + ' '.join(params)
        ret = self._doCommand(msg)
        try:
            ret = int(ret)
        except:
            try:
                ret = float(ret)
            except:
                try:
                    ret = str(ret)
                except:
                    ret = ERROR
        return ret

    def closeService(self):
        """
        Close bobot service
        """
        msg = 'QUIT'
        return self._doCommand(msg)

    def getButiaCount(self):
        """
        Gets the number of boards detected
        """
        msg = 'BUTIA_COUNT'
        ret = self._doCommand(msg)
        return int(ret)

    def getModulesList(self, normal=True):
        """
        returns a list of modules
        """
        msg = 'LIST'
        l = []
        ret = self._doCommand(msg)
        if not (ret == '' or ret == ERROR):
            l = ret.split(',')
        modules = []
        if not(normal):
            for m in l:
                modules.append(self._split_module(m))
        else:
            modules = l
        return modules

    def _split_module(self, mbn):
        """
        Split a modulename: module@board:port to (number, modulename, board)
        """
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

