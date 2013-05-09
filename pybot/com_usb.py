#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# USB comunication with USB4butia (USB4all) board
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

import usb
import usb.backend.libusb1 as libusb1
back_usb = libusb1.get_backend()

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
        self.dev = dev
        self.debug = True

    def _debug(self, message, err=''):
        if self.debug:
            print message, err

    def open_device(self):
        """
        Open the baseboard, configure the interface
        """
        try:
            if self.dev.is_kernel_driver_active(USB4ALL_INTERFACE) is True:
                self.dev.detach_kernel_driver(USB4ALL_INTERFACE)
            self.dev.set_configuration(USB4ALL_CONFIGURATION)
            usb.util.claim_interface(self.dev, USB4ALL_INTERFACE)
        except usb.USBError, err:
            self._debug('ERROR:com_usb:open_device', err)
            raise

    def close_device(self):
        """
        Close the comunication with the baseboard
        """
        try:
            usb.util.release_interface(self.dev, USB4ALL_INTERFACE)
        except Exception, err:
            self._debug('ERROR:com_usb:close_device', err)
        self.dev = None

    def read(self, size):
        """
        Read from the device length bytes
        """
        try:
            return self.dev.read(ADMIN_MODULE_OUT_ENDPOINT, size, USB4ALL_INTERFACE, TIMEOUT)
        except Exception, err:
            self._debug('ERROR:com_usb:read', err)
            raise
 
    def write(self, data):
        """
        Write in the device: data
        """
        try:
            return self.dev.write(ADMIN_MODULE_IN_ENDPOINT, data, USB4ALL_INTERFACE, TIMEOUT)
        except Exception, err:
            self._debug('ERROR:com_usb:write', err)
            raise

    def get_address(self):
        """
        Get unique address for the usb
        """
        address = ERROR
        try:
            address = self.dev.address
        except Exception, err:
            self._debug('ERROR:com_usb:get_address', err)
        return address

    def get_info(self):
        """
        Get the device info such as manufacturer, etc
        """
        try:
            names = usb.util.get_string(self.dev, 255, 1, None).encode('ascii')
            copy = usb.util.get_string(self.dev, 255, 2, None).encode('ascii')
            sn = usb.util.get_string(self.dev, 255, 3, None).encode('ascii')
            return [names, copy, sn]
        except Exception, err:
            self._debug('ERROR:com_usb:get_info', err)
            raise

def find():
    """
    List all busses and returns a list of baseboards detected
    """
    l = []
    for b in usb.core.find(find_all=True, backend=back_usb, idVendor=USB4ALL_VENDOR, idProduct=USB4ALL_PRODUCT):
        l.append(usb_device(b))
    return l

