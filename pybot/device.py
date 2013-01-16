#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# device abstraction for USB4butia
#

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

    def __init__(self, baseboard, name, handler):
        self.baseboard = baseboard
        self.name = name
        self.handler = handler
        if self.handler:
            self.handler_tosend = self.handler * 8
        self.functions = {}
        self.debug = True

    def add_functions(self, func_list):
        for f in func_list:
            self.functions[f['name']] = f

    def module_send(self, data, params_length, params):
        
        l = len(params)
        if not(l == params_length):
            if self.debug:
                print 'Incorrect lenght in params', data, params
            raise

        send_packet_length = 0x04 + l

        w = []
        w.append(self.handler_tosend)
        w.append(send_packet_length)
        w.append(NULL_BYTE)
        w.append(data)
        for p in params:
            w.append(p)

        size = self.baseboard.dev.write(w)

        if size == ERROR:
            if self.debug:
                print 'Error module_send write'
            raise

    def module_read(self, lenght = 0):
        if lenght == 0:
            raw = self.baseboard.dev.read(MAX_BYTES)
        else:
            raw = self.baseboard.dev.read(lenght)
        if raw == ERROR:
            if self.debug:
                print 'Error module_rad read'
            raise

        if raw[1] == 5:
            if raw[4] == 255:
                return -1
            else:
                return raw[4]
        elif raw[1] == 6:
            return raw[4] + raw[5] * 256
        else:
            ret = ''
            for r in raw[3:]:
                if not(r == 0):
                    ret = ret + chr(r)
            return ret

    def module_send_data(self, data):
        s = self.to_ord(data)
        send_packet_length = 0x04 + len(s)

        w = []
        w.append(self.handler_tosend)
        w.append(send_packet_length)
        w.append(NULL_BYTE)
        for d in s:
            w.append(d)

        size = self.baseboard.dev.write(w)

        if size == ERROR:
            if self.debug:
                print 'Error module_send write'
            raise

        return self.module_read(3 + len(s))

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
        size = self.baseboard.dev.write(w)

        if size == ERROR:
            if self.debug:
                print 'Error module_open write'
            raise

        raw = self.baseboard.dev.read(OPEN_RESPONSE_PACKET_SIZE)

        if raw == ERROR:
            if self.debug:
                print 'Error module_open read'
            raise

        h = raw[4]
        self.handler = h
        self.handler_tosend = self.handler * 8
        return h

    def has_function(self, func):
        return self.functions.has_key(func)

    def call_function(self, func, params):

        if self.functions[func].has_key('call'):
            raw = self.module_send(self.functions[func]['call'], self.functions[func]['params'], params)
            return self.module_read()
        else:
            return self.module_send_data(params)

    def to_ord(self, string):
        s = []
        for l in string:
            s.append(ord(l))
        s.append(0)
        
        return s

