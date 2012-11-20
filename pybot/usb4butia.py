#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# usb4butia main
#

import os
import imp
import com_usb
from baseboard import Baseboard


# BUTIA
RD_VERSION = 0x02
GET_VOLT = 0x03




class USB4butia():

    def __init__(self):
        self.listi = []
        self.default = ['admin', 'pnp', 'motors']
        self.hotplug = ['button', 'distanc', 'grey', 'light', 'volt', 'res']
        self.openables = ['gpio', 'lback', 'butia', 'hackp']
        self.drivers = {}

        device = com_usb.find()
        self.bb = Baseboard(device)
        handle = self.bb.open_device()


    def get_modules_list(self):
        if self.listi == []:
            self.get_listi()
        s = self.bb.get_handler_size()
        for m in self.listi:
            if not(m in self.hotplug) and not(m == 'port'):
                print m

        for m in range(1, s + 1):
            module_type = self.bb.get_handler_type(m)
            module_name = self.listi[module_type]
            print module_name + ':' +  str(m)

    def get_modules_and_handlers(self):
        if self.listi == []:
            self.get_listi()
        s = self.bb.get_handler_size()
        for m in self.listi:
            if not(m in self.hotplug) and not(m == 'port') and not(m == 'admin'):
                print m + ':255'

        for m in range(0, s + 1):
            module_type = self.bb.get_handler_type(m)
            module_name = self.listi[module_type]
            print module_name + ':' +  str(m)


    def get_listi(self):
        self.listi = []
        s = self.bb.get_user_modules_size()
        for m in range(s):
            name = self.bb.get_user_module_line(m)
            self.listi.append(name)
        return self.listi

    def get_driver_candidates(self):
        candidates = []
        tmp = os.listdir('drivers')
        tmp.sort()
        for d in tmp:
            if d.endswith('.py') and not (d == 'function.py'):
                name = d.strip('.py')
                candidates.append(name)
        return candidates
        

    def get_driver(self, driver):
        if not(self.drivers.has_key(driver)):
            can = self.get_driver_candidates()
            if driver in can:
                print 'Loading driver %s...' % driver
                r_path = os.path.join('drivers', driver + '.py')
                abs_path = os.path.abspath(r_path)
                f = None
                try:
                    f = imp.load_source(driver, abs_path)
                except:
                    print 'Cannot load %s' % driver
                if f and hasattr(f, 'FUNCTIONS'):
                    self.drivers[driver] = f.FUNCTIONS
                else:
                    print 'Driver not have FUNCTIONS'
            else:
                print 'driver not found'   
                    

    def callModule(self, modulename, number, function):
        pass


    def getButton(self, number=''):
        return self.callModule('button', number, 'getValue')




