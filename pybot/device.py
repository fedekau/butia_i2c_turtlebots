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

    def module_send(self, call, params_length, params):

        if not(type(params) == str):
            if not(len(params) == params_length):
                if self.debug:
                    print 'Incorrect lenght in params', params_length, params
        else:
            params = self.to_ord(params)

        send_packet_length = 0x04 + len(params)

        w = []
        w.append(self.handler_tosend)
        w.append(send_packet_length)
        w.append(NULL_BYTE)
        w.append(call)
        for p in params:
            w.append(p)

        size = self.baseboard.dev.write(w)

    def module_read(self):

        raw = self.baseboard.dev.read(MAX_BYTES)

        if self.debug:
            print 'device:module_rad return', raw

        if raw[1] == 5:
            if raw[4] == 255:
                return -1
            else:
                return raw[4]

        elif raw[1] == 6:
            return raw[4] + raw[5] * 256

        else:
            ret = ''
            for r in raw[4:]:
                if not(r == 0):
                    ret = ret + chr(r)
            return ret

    def module_open(self):

        module_name = self.to_ord(self.name)
        module_name.append(0)
        
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

        raw = self.baseboard.dev.read(OPEN_RESPONSE_PACKET_SIZE)

        if self.debug:
            print 'device:module_open return', raw

        h = raw[4]
        self.handler = h
        self.handler_tosend = self.handler * 8
        return h

    def has_function(self, func):
        return self.functions.has_key(func)

    def call_function(self, func, params):

        raw = self.module_send(self.functions[func]['call'], self.functions[func]['params'], params)
        return self.module_read()

    def to_ord(self, string):
        s = []
        for l in string:
            o = ord(l)
            if not(o == 0):
                s.append(o)
        return s

