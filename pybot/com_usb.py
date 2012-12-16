#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# USB comunication with USB4butia (USB4all) board
#

import usb

USB4ALL_VENDOR        = 0x04d8
USB4ALL_PRODUCT       = 0x000c
USB4ALL_CONFIGURATION = 1
USB4ALL_INTERFACE     = 0

ADMIN_MODULE_IN_ENDPOINT = 0x01
ADMIN_MODULE_OUT_ENDPOINT = 0x81

READ_HEADER_SIZE      = 3

TIMEOUT = 250

ERROR = -1

class usb_device():

    def __init__(self, dev):
        self.device = dev
        self.handle = None
        self.debug = True

    def open_device(self):
        try:
            self.handle = self.device.open()
            self.handle.setConfiguration(USB4ALL_CONFIGURATION)
            self.handle.claimInterface(USB4ALL_INTERFACE)
        except usb.USBError, err:
            if self.debug:
                print err
            self.handle = None
            raise
        return self.handle

    def close_device(self):
        try:
            if self.handle:
                self.handle.releaseInterface()
        except Exception, err:
            if self.debug:
                print err
            raise
        self.handle = None
        self.device = None

    def read(self, length):
        try:
            return self.handle.bulkRead(ADMIN_MODULE_OUT_ENDPOINT, length, TIMEOUT)
        except:
            if self.debug:
                print 'Exception in read usb'
            raise
 
    def write(self, data):
        try:
            return self.handle.bulkWrite(ADMIN_MODULE_IN_ENDPOINT, data, TIMEOUT)
        except:
            if self.debug:
                print 'Exception in write usb'
            raise

    def get_info(self):
        try:
            names = self.handle.getString(1, 255)
            copy = self.handle.getString(2, 255)
            sn = self.handle.getString(3, 255)
            return [names, copy, sn]
        except Exception, err:
            if self.debug:
                print 'Exception in get_info', err
            raise

def find():
    l = []
    for bus in usb.busses():
        for dev in bus.devices:
            if dev.idVendor == USB4ALL_VENDOR and dev.idProduct == USB4ALL_PRODUCT:
                l.append(usb_device(dev))
    return l

