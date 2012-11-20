#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# baseboard abstraction for USB4butia
#

import com_usb
from com_usb import usb_device

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
TIMEOUT = 250
MAX_RETRY = 5

ERROR = -1

class Baseboard(usb_device):

    def __init__(self, dev):
        usb_device.__init__(self, dev)

    def get_user_modules_size(self):
        w = []
        w.append(ADMIN_HANDLER_SEND_COMMAND)
        w.append(DEFAULT_PACKET_SIZE)
        w.append(NULL_BYTE)
        w.append(GET_USER_MODULES_SIZE_COMMAND)
        size = self.write(ADMIN_MODULE_IN_ENDPOINT, w, TIMEOUT)

        if size == ERROR:
            if self.debug:
                print 'Error get_user_modules_size write'
            return ERROR

        raw = self.read(ADMIN_MODULE_OUT_ENDPOINT, GET_USER_MODULE_LINE_PACKET_SIZE, TIMEOUT)

        if raw == ERROR:
            if self.debug:
                print 'Error get_user_modules_size read'
            return ERROR

        return raw[4]

    def get_user_module_line(self, index):
        
        if index < 0:
            if self.debug:
                print 'Error index get_user_module_line'
            return ERROR

        w = []
        w.append(ADMIN_HANDLER_SEND_COMMAND)
        w.append(GET_USER_MODULE_LINE_PACKET_SIZE)
        w.append(NULL_BYTE)
        w.append(GET_USER_MODULE_LINE_COMMAND)
        w.append(index)
        size = self.write(ADMIN_MODULE_IN_ENDPOINT, w, TIMEOUT)

        if size == ERROR:
            if self.debug:
                print 'Error get_user_module_line write'
            return ERROR

        raw = self.read(ADMIN_MODULE_OUT_ENDPOINT, GET_LINE_RESPONSE_PACKET_SIZE, TIMEOUT)

        if raw == ERROR:
            if self.debug:
                print 'Error get_user_module_line read'
            return ERROR

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
        size = self.write(ADMIN_MODULE_IN_ENDPOINT, w, TIMEOUT)

        if size == ERROR:
            if self.debug:
                print 'Error get_handler_size write'
            return ERROR

        raw = self.read(ADMIN_MODULE_OUT_ENDPOINT, GET_HANDLER_RESPONSE_PACKET_SIZE, TIMEOUT)

        if raw == ERROR:
            if self.debug:
                print 'Error get_handler_size read'
            return ERROR

        return raw[4]

    def get_handler_type(self, index):
        w = []
        w.append(ADMIN_HANDLER_SEND_COMMAND)
        w.append(GET_HANDLER_TYPE_PACKET_SIZE)
        w.append(NULL_BYTE)
        w.append(GET_HANDLER_TYPE_COMMAND)
        w.append(index)
        size = self.write(ADMIN_MODULE_IN_ENDPOINT, w, TIMEOUT)

        if size == ERROR:
            if self.debug:
                print 'Error get_handler_type write'
            return ERROR

        raw = self.read(ADMIN_MODULE_OUT_ENDPOINT, GET_HANDLER_RESPONSE_PACKET_SIZE, TIMEOUT)

        if raw == ERROR:
            if self.debug:
                print 'Error get_handler_type read'
            return ERROR

        return raw[4]

    def switch_to_bootloader(self):
        w = []
        w.append(ADMIN_HANDLER_SEND_COMMAND)
        w.append(DEFAULT_PACKET_SIZE)
        w.append(NULL_BYTE)
        w.append(SWITCH_TO_BOOT_BASE_BOARD_COMMAND)
        size = self.write(ADMIN_MODULE_IN_ENDPOINT, w, TIMEOUT)

        if size == ERROR:
            if self.debug:
                print 'Error switch_to_bootloader write'
            return ERROR

    def reset(self):
        w = []
        w.append(ADMIN_HANDLER_SEND_COMMAND)
        w.append(DEFAULT_PACKET_SIZE)
        w.append(NULL_BYTE)
        w.append(RESET_BASE_BOARD_COMMAND)
        size = self.write(ADMIN_MODULE_IN_ENDPOINT, w, TIMEOUT)

        if size == ERROR:
            if self.debug:
                print 'Error reset write'
            return ERROR

    def force_close_all(self):
        w = []
        w.append(ADMIN_HANDLER_SEND_COMMAND)
        w.append(DEFAULT_PACKET_SIZE)
        w.append(NULL_BYTE)
        w.append(CLOSEALL_BASE_BOARD_COMMAND)
        size = self.write(ADMIN_MODULE_IN_ENDPOINT, w, TIMEOUT)

        if size == ERROR:
            if self.debug:
                print 'Error force_close_all write'
            return ERROR

        raw = self.read(ADMIN_MODULE_OUT_ENDPOINT, CLOSEALL_BASE_BOARD_RESPONSE_PACKET_SIZE, TIMEOUT)

        if raw == ERROR:
            if self.debug:
                print 'Error force_close_all read'
            return ERROR

        return raw[4]


