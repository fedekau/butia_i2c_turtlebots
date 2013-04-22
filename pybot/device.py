#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Device abstraction for USB4butia
#
# Copyright (c) 2012-2013 Butiá Team butia@fing.edu.uy 
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


NULL_BYTE = 0x00
OPEN_COMMAND = 0x00
CLOSE_COMMAND = 0x01
HEADER_PACKET_SIZE = 0x06
ADMIN_HANDLER_SEND_COMMAND = 0x00
OPEN_RESPONSE_PACKET_SIZE = 5
CLOSE_RESPONSE_PACKET_SIZE = 2
READ_HEADER_SIZE = 3
MAX_BYTES = 64

ERROR = -1

class Device():

    def __init__(self, baseboard, name, handler=None, func=None):
        self.baseboard = baseboard
        self.name = name
        self.handler = handler
        if not(self.handler == None):
            self.handler_tosend = self.handler * 8
        else:
            self.handler_tosend = None
        self.functions = func
        self.debug = False

    def _debug(self, message, err=''):
        if self.debug:
            print message, err

    def send(self, msg):
        """
        Send to the device the specifiy call and parameters
        """
        w = [self.handler_tosend, 0x03 + len(msg), NULL_BYTE]
        self.baseboard.dev.write(w + msg)

    def read(self, lenght):
        """
        Read the device data
        """
        raw = self.baseboard.dev.read(0x03 + lenght)
        self._debug('device:read', raw)
        return raw[3:]

    def module_open(self):
        """
        Open this device. Return the handler
        """
        module_name = self.to_ord(self.name)
        module_name.append(NULL_BYTE)

        w = [ADMIN_HANDLER_SEND_COMMAND]
        w.append(HEADER_PACKET_SIZE + len(module_name))
        w.append(NULL_BYTE)
        w.append(OPEN_COMMAND)
        w.append(0x01)
        w.append(0x01)
        self.baseboard.dev.write(w + module_name)

        raw = self.baseboard.dev.read(OPEN_RESPONSE_PACKET_SIZE)

        self._debug('device:module_open', raw)

        if not(raw[4] == 255):
            self.handler = raw[4]
            self.handler_tosend = self.handler * 8
            return self.handler
        else:
            self._debug('device:module_open:cannot open module:', self.name)
            return 255

    def has_function(self, func):
        """
        Check if this device has func function
        """
        return hasattr(self.functions, func)

    def call_function(self, func, params):
        """
        Call specify func function with params parameters
        """
        f = getattr(self.functions, func)
        if self.name == 'lback':
            return f(self, params)
        else:
            par = []
            for e in params:
                par.append(int(e))
            if func == 'sendPacket':
                return f(self, par)
            else:
                return f(self, *par)

    def to_ord(self, string):
        """
        Useful function to convert characters into ordinal Unicode
        """
        s = []
        for l in string:
            o = ord(l)
            if not(o == 0):
                s.append(o)
        return s

