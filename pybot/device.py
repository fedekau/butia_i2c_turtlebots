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

OPEN_RESPONSE_PACKET_SIZE = 5
CLOSE_RESPONSE_PACKET_SIZE = 2

READ_HEADER_SIZE = 3

TIMEOUT = 250


class Device():

    def __init__(self, baseboard, name, hotplug, functions = None):
        self.baseboard = baseboard
        self.name = name
        self.hotplug = hotplug
        self.functions = functions

    def module_send(self, handler, data):
        
        user_module_handler_send_command = handler * 8
        send_packet_length = 0x04

        w = []
        w.append(user_module_handler_send_command)
        w.append(send_packet_length)
        w.append(NULL_BYTE)
        w.append(data)
        print w
        size = self.baseboard.write(ADMIN_MODULE_IN_ENDPOINT, w, TIMEOUT)

    def module_read(self, lenght):

        raw = self.baseboard.read(ADMIN_MODULE_OUT_ENDPOINT, READ_HEADER_SIZE  + lenght, TIMEOUT)
        print raw
        l = []
        for i in range(READ_HEADER_SIZE, READ_HEADER_SIZE + lenght):
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

        raw = self.baseboard.read(ADMIN_MODULE_OUT_ENDPOINT, OPEN_RESPONSE_PACKET_SIZE, TIMEOUT)

        return raw

    def to_ord(self, string):
        s = []
        for l in string:
            s.append(ord(l))
        s.append(0)
        
        return s

