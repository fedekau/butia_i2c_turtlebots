#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# device abstraction for USB4butia
#

NULL_BYTE = 0x00
OPEN_COMMAND = 0x00
CLOSE_COMMAND = 0x01
HEADER_PACKET_SIZE = 0x06

ADMIN_MODULE_IN_ENDPOINT = 0x01
ADMIN_MODULE_OUT_ENDPOINT = 0x81
ADMIN_HANDLER_SEND_COMMAND = 0x00

OPEN_RESPONSE_PACKET_SIZE = 5
CLOSE_RESPONSE_PACKET_SIZE = 2

READ_HEADER_SIZE = 3

TIMEOUT = 250

ERROR = -1

class Device():

    def __init__(self, baseboard, name, handler, functions = None):
        self.baseboard = baseboard
        self.name = name
        self.handler = handler
        self.functions = functions

    def add_functions(self, func_list):
        self.functions = {}
        for f in func_list:
            self.functions[f['name']] = f

    def module_send(self, data, params):
        
        user_module_handler_send_command = self.handler * 8
        l = len(params)
        send_packet_length = 0x04 + l

        w = []
        w.append(user_module_handler_send_command)
        w.append(send_packet_length)
        w.append(NULL_BYTE)
        w.append(data)
        for p in params:
            w.append(p)

        size = self.baseboard.write(ADMIN_MODULE_IN_ENDPOINT, w, TIMEOUT)

        if size == ERROR:
            print 'Error module_send write'
            return ERROR

    def module_read(self, lenght):
        raw = self.baseboard.read(ADMIN_MODULE_OUT_ENDPOINT, READ_HEADER_SIZE  + lenght, TIMEOUT)
        if raw == ERROR:
            print 'Error module_rad read'
            return ERROR

        l = []
        for i in range(READ_HEADER_SIZE + 1, READ_HEADER_SIZE + lenght):
            l.append(raw[i])
        return l

    def module_open(self):
        
        module_name = self.to_ord(self.name)
        
        open_packet_length = HEADER_PACKET_SIZE + len(module_name) 

        module_in_endpoint  = 0x01
        module_out_endpoint = 0x01

        w = []
        w.append(ADMIN_HANDLER_SEND_COMMAND)
        w.append(open_packet_length)
        w.append(NULL_BYTE)
        w.append(OPEN_COMMAND)
        w.append(module_in_endpoint)
        w.append(module_out_endpoint)
        w = w + module_name
        size = self.baseboard.write(ADMIN_MODULE_IN_ENDPOINT, w, TIMEOUT)

        if size == ERROR:
            print 'Error module_open write'
            return ERROR

        raw = self.baseboard.read(ADMIN_MODULE_OUT_ENDPOINT, OPEN_RESPONSE_PACKET_SIZE, TIMEOUT)

        if raw == ERROR:
            print 'Error module_open read'
            return ERROR

        h = raw[4]
        self.handler = h
        return h

    def has_function(self, func):
        if not(self.functions == None):
            return self.functions.has_key(func)
        else:
            return False

    def call_function(self, func, params):
        f = self.functions[func]

        raw = self.module_send(f['call'], params)
        if raw == ERROR:
            return ERROR

        raw = self.module_read(f['read'])
        if raw == ERROR:
            return ERROR

        elif len(raw) == 1:
            return raw[0]
        elif len(raw) == 2:
            return raw[0] + raw[1] * 256

    def to_ord(self, string):
        s = []
        for l in string:
            s.append(ord(l))
        s.append(0)
        
        return s

