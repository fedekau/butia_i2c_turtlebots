#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# usb4butia main
#

import com_usb
from baseboard import Baseboard

# BUTIA
RD_VERSION = 0x02
GET_VOLT = 0x03




class USB4butia():

    def __init__(self):
        self.listi = []
        self.hotplug = ['button', 'distanc', 'grey', 'light', 'volt', 'res']
        self.openables = ['']
        device = com_usb.find()
        self.bb = Baseboard(device)
        handle = self.bb.open_device()


    def get_modules_list(self):
        if self.listi == []:
            self.bb.get_listi()
        s = self.bb.get_handler_size()
        for m in self.listi:
            if not(m in self.hotplug) and not(m == 'port'):
                print m

        for m in range(1, s+1):
            module_type = self.bb.get_handler_type(m)
            module_name = self.listi[module_type]
            print module_name + ':' +  str(m)


    def get_listi(self):
        self.listi = []
        s = self.bb.get_user_modules_size()
        for m in range(s):
            name = self.bb.get_user_module_line(m)
            t = self.bb.get_handler_type(m)
            self.listi.append(name)
            #print name  #, t
        return self.listi










