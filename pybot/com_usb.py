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

READ_HEADER_SIZE      = 3


class usb_device():

    def __init__(self, dev):
        self.device = dev
        self.handle = None

    def open_device(self):
        if not self.device:
            print "Unable to find device!"
            return None
        try:
            self.handle = self.device.open()
            self.handle.setConfiguration(USB4ALL_CONFIGURATION)
            self.handle.claimInterface(USB4ALL_INTERFACE)
        except usb.USBError, err:
            print err
            self.handle = None
        return self.handle

    def close_device(self):
        try:
            self.handle.releaseInterface()
        except Exception, err:
            print err
        self.handle = None
        self.device = None

    def read(self, endpoint, length, timeout = 0):
        return self.handle.bulkRead(endpoint, length, timeout)
 
    def write(self, endpoint, data, timeout = 0):
        return self.handle.bulkWrite(endpoint, data, timeout)

    def get_info(self):
        names = self.handle.getString(1, 255)
        copy = self.handle.getString(2, 255)
        sn = self.handle.getString(3, 255)
        return [names, copy, sn]


def find():
    for bus in usb.busses():
        for dev in bus.devices:
            if dev.idVendor == USB4ALL_VENDOR and dev.idProduct == USB4ALL_PRODUCT:
                return dev

