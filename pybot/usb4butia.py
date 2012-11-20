#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# usb4butia main
#

import os
import sys
import imp
import com_usb
from baseboard import Baseboard
from device import Device

PATH_DRIVERS = 'plugins/butia/pybot/drivers'

ERROR = -1

class USB4Butia():

    def __init__(self):
        
        self.default = ['admin', 'pnp']
        self.hotplug = ['button', 'distanc', 'grey', 'light', 'volt', 'res', 'port']
        self.openables = ['motors', 'gpio', 'lback', 'butia', 'hackp']
        self.listi = []
        self.openables_loaded = []
        self.drivers_loaded = {}
        self.inited_n = {}
        self.inited_d = {}

        device = com_usb.find()
        self.bb = Baseboard(device)
        self.handle = self.bb.open_device()
        self.get_modules_list()

    def get_modules_list(self):
        modules = []
        if self.handle:
            if self.listi == []:
                self.get_listi()

            s = self.bb.get_handler_size()
            self.inited_n = {}
            self.inited_d = {}
            for m in range(1, s + 1):
                module_type = self.bb.get_handler_type(m)
                module_name = self.listi[module_type]
                modules.append(module_name + ':' +  str(m))

                if not(module_name == 'port'):
                    self.inited_n[m] = module_name
                    self.inited_d[m] = Device(self.bb, module_name, m)


            values = self.inited_n.values()
            for m in self.listi:
                if not(m in values) and not(m in self.hotplug):
                    modules.append(m)

        return modules

    def get_listi(self):
        self.listi = []
        if self.handle:
            s = self.bb.get_user_modules_size()
            for m in range(s):
                name = self.bb.get_user_module_line(m)
                self.listi.append(name)
        return self.listi

    def get_driver_candidates(self):
        candidates = []
        tmp = os.listdir(PATH_DRIVERS)
        tmp.sort()
        for d in tmp:
            if d.endswith('.py') and not (d == 'function.py'):
                name = d.replace('.py', '')
                candidates.append(name)
        return candidates
        

    def get_driver(self, driver):
        can = self.get_driver_candidates()
        if driver in can:
            print 'Loading driver %s...' % driver
            r_path = os.path.join(PATH_DRIVERS, driver + '.py')
            abs_path = os.path.abspath(r_path)
            f = None
            try:
                f = imp.load_source(driver, abs_path)
            except:
                print 'Cannot load %s' % driver
            if f and hasattr(f, 'FUNCTIONS'):
                self.drivers_loaded[driver] = f.FUNCTIONS
                for d in self.inited_d.values():
                    if d.name == driver:
                        d.add_functions(f.FUNCTIONS)
            else:
                print 'Driver not have FUNCTIONS'
        else:
            print 'driver not found' 


    def call_aux(self, modulename, number, function, params):
        
        device = self.inited_d[number]
        if not(device.has_function(function)):
            f = self.drivers_loaded[modulename]
            device.add_functions(f)
        if device.has_function(function):
            return device.call_function(function, params)
        else:
            print 'Missing function %s', function


    def callModule(self, modulename, number, function, params = []):

        if self.handle:

            if not(modulename in self.drivers_loaded):
                self.get_driver(modulename)

            if self.inited_n.has_key(number) and (self.inited_d[number].name == modulename):

                return self.call_aux(modulename, number, function, params)

            else:
                mods = self.get_modules_list()
                if modulename in self.openables:
                    if not(modulename in self.openables_loaded):
                        self.openables_loaded.append(modulename)
                        dev = Device(self.bb, modulename, None)
                        h = dev.module_open()
                        dev.handler = h
                        self.inited_n[h] = modulename
                        self.inited_d[h] = dev
                        f = self.drivers_loaded[modulename]
                        dev.add_functions(f)
                        number = h
                    else:
                        number = self.search_handler(mods, modulename)
                    if number == ERROR:
                        return ERROR
                    return self.call_aux(modulename, number, function, params)
                else:
                    print 'no open and no openable'
                    return -1
                
        else:
            return -1

    def search_handler(self, l, module):
        ll = self.list_2_module_and_port(l)
        for e in ll:
            if e[1] == module:
                return int(e[0])
        return -1

    def list_2_module_and_port(self, l):
        r = []
        for e in l:
            try:
                module, port = e.split(':')
                if module in self.openables:
                    r.append((port, module))
            except:
                pass
        return r

    def reconnect(self):
        pass

    def refresh(self):
        info = self.bb.get_info()
        if info == ERROR:
            self.bb.close_device()
            device = com_usb.find()
            self.bb = Baseboard(device)
            self.handle = self.bb.open_device()
            self.listi = []
            self.openables_loaded = []
            self.drivers_loaded = {}
            self.inited_n = {}
            self.inited_d = {}
            self.get_modules_list()

    def close(self):
        self.bb.close_device()

    def closeService(self):
        pass

    def isPresent(self, module_name):
        module_list = self.get_modules_list()
        return (module_name in module_list)

    def loopBack(self, data):
        pass

    def set2MotorSpeed(self, leftSense = '0', leftSpeed = '0', rightSense = '0', rightSpeed = '0'):
        msg = [leftSense, int(leftSpeed / 256.0), leftSpeed % 256, rightSense, int(rightSpeed / 256.0) , rightSpeed % 256]
        return self.callModule('motors', None, 'setvel2mtr', msg)
     
    def setMotorSpeed(self, idMotor = '0', sense = '0', speed = '0'):
        msg = idMotor + ' ' + sense + ' ' + speed
        return self.callModule('motors', None, 'setvelmtr', msg)

     
    def getBatteryCharge(self):
        return self.callModule('butia', None, 'get_volt')

    def getVersion(self):
        return self.callModule('butia', None, 'read_ver')

    def getButton(self, number=''):
        return self.callModule('button', number, 'getValue')
    
    def getAmbientLight(self, number=''):
        return self.callModule('light', number, 'getValue')

    def getDistance(self, number=''):
        return self.callModule('distanc', number, 'getValue')

    def getGrayScale(self, number=''):
        return self.callModule('grey', number, 'getValue')

    def getResistance(self, number=''):
        vcc = 65535
        raw = self.callModule('res', number, 'getValue')
        if not(raw == -1):
            return raw * 6800 / (vcc - raw)
        return raw

    def getVoltaje(self, number=''):
        vcc = 65535
        raw = self.callModule('volt', number, 'getValue')
        if not(raw == -1):
            return raw * 5 / vcc
        return raw

