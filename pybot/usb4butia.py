#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# usb4butia main
#

import os
import imp
import com_usb
from baseboard import Baseboard
from device import Device

# BUTIA
RD_VERSION = 0x02
GET_VOLT = 0x03




class USB4Butia():

    def __init__(self):
        self.listi = []
        self.default = ['admin', 'pnp', 'motors']
        self.hotplug = ['button', 'distanc', 'grey', 'light', 'volt', 'res']
        self.openables = ['gpio', 'lback', 'butia', 'hackp']
        self.drivers_loaded = []
        self.inited_n = {}
        self.inited_d = {}

        device = com_usb.find()
        self.bb = Baseboard(device)
        handle = self.bb.open_device()

        self.get_modules_and_handlers()

    def get_modules_list(self):
        modules = []
        if self.listi == []:
            self.get_listi()
        s = self.bb.get_handler_size()
        for m in self.listi:
            if not(m in self.hotplug) and not(m == 'port'):
                modules.append(m)

        for m in range(1, s + 1):
            module_type = self.bb.get_handler_type(m)
            module_name = self.listi[module_type]
            #print module_name + ':' +  str(m)
            modules.append(module_name + ':' +  str(m))
        return modules

    def get_modules_and_handlers(self):
        self.inited_n = {}
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
            self.inited_n[m] = module_name
            self.inited_d[m] = Device(self.bb, module_name, m)
            

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
                name = d.replace('.py', '')
                candidates.append(name)
        return candidates
        

    def get_driver(self, driver):
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
                self.drivers_loaded.append(driver)
                for d in self.inited_d.values():
                    if d.name == driver:
                        d.add_functions(f.FUNCTIONS)
            else:
                print 'Driver not have FUNCTIONS'
        else:
            print 'driver not found' 
                    

    def callModule(self, modulename, number, function):
        if not(modulename in self.drivers_loaded):
            self.get_driver(modulename)
        if modulename in self.drivers_loaded:
            if self.inited_n.has_key(number):
                device = self.inited_d[number]
                if device.has_function(function):
                    print device.call_function(function)
                else:
                    print 'Missing function %s' % function
            else:
                print 'missing handler'
        

    def reconnect(self):
        pass

    def refresh(self):
        pass

    def close(self):
        pass

    def closeService(self):
        pass

    def isPresent(self, module_name):
        module_list = self.get_modules_list()
        return (module_name in module_list)

    def loopBack(self, data):
        pass

    def set2MotorSpeed(self, leftSense = '0', leftSpeed = '0', rightSense = '0', rightSpeed = '0'):
        msg = leftSense + ' ' + leftSpeed + ' ' + rightSense + ' ' + rightSpeed
        return self.callModule('motors', 'setvel2mtr', msg)
     
    def setMotorSpeed(self, idMotor = '0', sense = '0', speed = '0'):
        msg = idMotor + ' ' + sense + ' ' + speed
        return self.callModule('motors', 'setvelmtr', msg)

     
    def getBatteryCharge(self):
        return self.callModule('butia', None, 'get_volt')

    def getVersion(self):
        return self.callModule('butia', 'read_ver')

    def getButton(self, number=''):
        return self.callModule('button', number, 'getValue')
    
    def getButton(self, number=''):
        return self.callModule('button', number, 'getValue')

    def getAmbientLight(self, number=''):
        return self.callModule('light', number, 'getValue')

    def getDistance(self, number=''):
        return self.callModule('distanc', number, 'getValue')

    def getGrayScale(self, number=''):
        return self.callModule('grey', number, 'getValue')

    def getResistance(self, number=''):
        return self.callModule('res', number, 'getValue')

    def getVoltaje(self, number=''):
        return self.callModule('volt', number, 'getValue')



