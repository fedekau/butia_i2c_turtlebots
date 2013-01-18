#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# baseboard abstraction for USB4butia
#

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

MAX_RETRY = 5

ERROR = -1

class Baseboard():

    def __init__(self, dev):
        self.dev = dev
        self.debug = self.dev.debug
        self.devices = {}

    def open_baseboard(self):
        self.dev.open_device()

    def close_baseboard(self):
        self.dev.close_device()

    def get_info(self):
        return self.dev.get_info()

    def add_device(self, handler, device):
        self.devices[handler] = device

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

        if size == ERROR:
            if self.debug:
                print 'Error get_user_modules_size write'
            raise

        raw = self.dev.read(GET_USER_MODULE_LINE_PACKET_SIZE)

        if raw == ERROR:
            if self.debug:
                print 'Error get_user_modules_size read'
            raise

        return raw[4]

    def get_user_module_line(self, index):
        
        if index < 0:
            if self.debug:
                print 'Error index get_user_module_line'
            raise

        w = []
        w.append(ADMIN_HANDLER_SEND_COMMAND)
        w.append(GET_USER_MODULE_LINE_PACKET_SIZE)
        w.append(NULL_BYTE)
        w.append(GET_USER_MODULE_LINE_COMMAND)
        w.append(index)
        size = self.dev.write(w)

        if size == ERROR:
            if self.debug:
                print 'Error get_user_module_line write'
            raise

        raw = self.dev.read(GET_LINE_RESPONSE_PACKET_SIZE)

        if raw == ERROR:
            if self.debug:
                print 'Error get_user_module_line read'
            raise

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

        if size == ERROR:
            if self.debug:
                print 'Error get_handler_size write'
            raise

        raw = self.dev.read(GET_HANDLER_RESPONSE_PACKET_SIZE)

        if raw == ERROR:
            if self.debug:
                print 'Error get_handler_size read'
            raise

        return raw[4]

    def get_handler_type(self, index):
        w = []
        w.append(ADMIN_HANDLER_SEND_COMMAND)
        w.append(GET_HANDLER_TYPE_PACKET_SIZE)
        w.append(NULL_BYTE)
        w.append(GET_HANDLER_TYPE_COMMAND)
        w.append(index)
        size = self.dev.write(w)

        if size == ERROR:
            if self.debug:
                print 'Error get_handler_type write'
            raise

        raw = self.dev.read(GET_HANDLER_RESPONSE_PACKET_SIZE)

        if raw == ERROR:
            if self.debug:
                print 'Error get_handler_type read'
            raise

        return raw[4]

    def switch_to_bootloader(self):
        w = []
        w.append(ADMIN_HANDLER_SEND_COMMAND)
        w.append(DEFAULT_PACKET_SIZE)
        w.append(NULL_BYTE)
        w.append(SWITCH_TO_BOOT_BASE_BOARD_COMMAND)
        size = self.dev.write(w)

        if size == ERROR:
            if self.debug:
                print 'Error switch_to_bootloader write'
            raise

    def reset(self):
        w = []
        w.append(ADMIN_HANDLER_SEND_COMMAND)
        w.append(DEFAULT_PACKET_SIZE)
        w.append(NULL_BYTE)
        w.append(RESET_BASE_BOARD_COMMAND)
        size = self.dev.write(w)

        if size == ERROR:
            if self.debug:
                print 'Error reset write'
            raise

    def force_close_all(self):
        w = []
        w.append(ADMIN_HANDLER_SEND_COMMAND)
        w.append(DEFAULT_PACKET_SIZE)
        w.append(NULL_BYTE)
        w.append(CLOSEALL_BASE_BOARD_COMMAND)
        size = self.dev.write(w)

        if size == ERROR:
            if self.debug:
                print 'Error force_close_all write'
            raise

        raw = self.dev.read(CLOSEALL_BASE_BOARD_RESPONSE_PACKET_SIZE)

        if raw == ERROR:
            if self.debug:
                print 'Error force_close_all read'
            raise

        return raw[4]


