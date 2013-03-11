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
from butia_functions import functions

ERROR = -1

PYBOT_HOST = 'localhost'
PYBOT_PORT = 2009

class robot(functions):
    
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
        except Exception, e:
            if hasattr(e, 'errno'):
                if e.errno == errno.EPIPE:
                    self.reconnect()
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
            number = '0'
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
                try:
                    ret = str(ret)
                except:
                    ret = ERROR
        return ret

    # Close bobot service
    def closeService(self):
        msg = 'QUIT'
        return self.doCommand(msg)

    def get_butia_count(self):
        msg = 'BUTIA_COUNT'
        ret = self.doCommand(msg)
        return int(ret)

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

