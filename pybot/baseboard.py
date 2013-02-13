#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Baseboard abstraction for USB4butia
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
DEFAULT_PACKET_SIZE = 0x04
GET_USER_MODULES_SIZE_COMMAND = 0x05
GET_USER_MODULE_LINE_COMMAND = 0x06
GET_HANDLER_SIZE_COMMAND = 0x0A
GET_HANDLER_TYPE_COMMAND = 0x0B
ADMIN_HANDLER_SEND_COMMAND = 0x00
CLOSEALL_BASE_BOARD_COMMAND = 0x07
SWITCH_TO_BOOT_BASE_BOARD_COMMAND = 0x09
RESET_BASE_BOARD_COMMAND = 0xFF

ADMIN_MODULE_IN_ENDPOINT = 0x01
ADMIN_MODULE_OUT_ENDPOINT = 0x81
GET_USER_MODULE_LINE_PACKET_SIZE = 0x05

GET_LINES_RESPONSE_PACKET_SIZE = 5
GET_LINE_RESPONSE_PACKET_SIZE = 12
GET_HANDLER_TYPE_PACKET_SIZE = 5
GET_HANDLER_RESPONSE_PACKET_SIZE = 5
CLOSEALL_BASE_BOARD_RESPONSE_PACKET_SIZE = 5

ERROR = -1

class Baseboard():

    def __init__(self, dev):
        self.dev = dev
        self.debug = False
        self.listi = {}
        self.devices = {}
        self.openables_loaded = []

    def open_baseboard(self):
        self.dev.open_device()

    def close_baseboard(self):
        self.dev.close_device()

    def get_info(self):
        return self.dev.get_info()

    def add_device(self, handler, device):
        self.devices[handler] = device

    def add_openable_loaded(self, name):
        if not(name in self.openables_loaded):
            self.openables_loaded.append(name)

    def get_openables_loaded(self):
        return self.openables_loaded

    def reset_openables_loaded(self):
        self.openables_loaded = []

    def add_to_listi(self, number, name):
        self.listi[number] = name

    def get_listi(self):
        if (self.listi == {}):
            self.generate_listi()
        return self.listi

    def generate_listi(self):
        try:
            s = self.get_user_modules_size()
            for m in range(s):
                name = self.get_user_module_line(m)
                self.listi[m] = name
        except:
            if self.debug:
                print 'error listi'

    def get_device_handler(self, device):
        for e in self.devices:
            if self.devices[e].name == device:
                return e
        return ERROR

    def get_device_name(self, handler):
        if self.devices.has_key(handler):
            return self.devices[handler].name
        else:
            return ''

    def get_user_modules_size(self):
        w = []
        w.append(ADMIN_HANDLER_SEND_COMMAND)
        w.append(DEFAULT_PACKET_SIZE)
        w.append(NULL_BYTE)
        w.append(GET_USER_MODULES_SIZE_COMMAND)
        size = self.dev.write(w)

        raw = self.dev.read(GET_USER_MODULE_LINE_PACKET_SIZE)
        
        if self.debug:
            print 'baseboard:get_user_modules_size return', raw

        return raw[4]

    def get_user_module_line(self, index):
        w = []
        w.append(ADMIN_HANDLER_SEND_COMMAND)
        w.append(GET_USER_MODULE_LINE_PACKET_SIZE)
        w.append(NULL_BYTE)
        w.append(GET_USER_MODULE_LINE_COMMAND)
        w.append(index)
        size = self.dev.write(w)

        raw = self.dev.read(GET_LINE_RESPONSE_PACKET_SIZE)

        if self.debug:
            print 'baseboard:get_user_module_line return', raw

        c = raw[4:len(raw)]
        t = ''
        for e in c:
            if not(e == NULL_BYTE):
                t = t + chr(e)

        return t

    def get_handler_size(self):
        w = []
        w.append(ADMIN_HANDLER_SEND_COMMAND)
        w.append(DEFAULT_PACKET_SIZE)
        w.append(NULL_BYTE)
        w.append(GET_HANDLER_SIZE_COMMAND)
        size = self.dev.write(w)

        raw = self.dev.read(GET_HANDLER_RESPONSE_PACKET_SIZE)

        if self.debug:
            print 'baseboard:get_handler_size return', raw

        return raw[4]

    def get_handler_type(self, index):
        w = []
        w.append(ADMIN_HANDLER_SEND_COMMAND)
        w.append(GET_HANDLER_TYPE_PACKET_SIZE)
        w.append(NULL_BYTE)
        w.append(GET_HANDLER_TYPE_COMMAND)
        w.append(index)
        size = self.dev.write(w)

        raw = self.dev.read(GET_HANDLER_RESPONSE_PACKET_SIZE)

        if self.debug:
            print 'baseboard:get_handler_type return', raw

        return raw[4]

    def switch_to_bootloader(self):
        w = []
        w.append(ADMIN_HANDLER_SEND_COMMAND)
        w.append(DEFAULT_PACKET_SIZE)
        w.append(NULL_BYTE)
        w.append(SWITCH_TO_BOOT_BASE_BOARD_COMMAND)
        size = self.dev.write(w)

    def reset(self):
        w = []
        w.append(ADMIN_HANDLER_SEND_COMMAND)
        w.append(DEFAULT_PACKET_SIZE)
        w.append(NULL_BYTE)
        w.append(RESET_BASE_BOARD_COMMAND)
        size = self.dev.write(w)

    def force_close_all(self):
        w = []
        w.append(ADMIN_HANDLER_SEND_COMMAND)
        w.append(DEFAULT_PACKET_SIZE)
        w.append(NULL_BYTE)
        w.append(CLOSEALL_BASE_BOARD_COMMAND)
        size = self.dev.write(w)

        raw = self.dev.read(CLOSEALL_BASE_BOARD_RESPONSE_PACKET_SIZE)

        if self.debug:
            print 'baseboard:force_close_all return', raw

        return raw[4]


