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
        self.hotplug = []
        self.openables = []
        self.openables_loaded = {}
        self.drivers_loaded = {}
        self.bb = []
        self.find_butias()

    def find_butias(self):
        devices = com_usb.find()
        for dev in devices:
            b = Baseboard(dev)
            try:
                b.open_baseboard()
                self.bb.append(b)
            except:
                print 'error open baseboard'
        self.get_modules_list()

    def get_modules_list(self):
        modules = []

        for i, b in enumerate(self.bb):
            try:
                self.get_listis()
                loaded = []
                s = b.get_handler_size()
                print 'handler_size', s


                devices = {}
                listi = self.listis[b]
                for m in range(0, s + 1):
                    module_type = b.get_handler_type(m)
                    module_name = listi[module_type]
                    modules.append(module_name + '@' + str(i) + ':' +  str(m))

                    if not(module_name == 'port'):
                        #print 'module_name', module_name
                        if module_name in self.openables:
                            loaded.append(module_name)

                        d = Device(b, module_name, m)
                        b.add_device(m, d)
                        devices[m] = d
                    
                self.openables_loaded[b] = loaded
       
            except Exception, err:
                print 'error module list', err

        return modules

    def get_listis(self):
        self.listis = {}
        for b in self.bb:
            try:
                l = []
                s = b.get_user_modules_size()
                for m in range(s):
                    name = b.get_user_module_line(m)
                    l.append(name)
                self.listis[b] = l
            except:
                print 'error listi'
        return self.listis

    def get_driver_candidates(self):
        # normal drivers
        tmp = os.listdir(PATH_DRIVERS)
        tmp.sort()
        for d in tmp:
            if d.endswith('.py'):
                name = d.replace('.py', '')
                self.openables.append(name)
        # hotplug drivers
        path = os.path.join(PATH_DRIVERS, 'hotplug')
        tmp = os.listdir(path)
        tmp.sort()
        for d in tmp:
            if d.endswith('.py'):
                name = d.replace('.py', '')
                self.hotplug.append(name)
        return self.hotplug + self.openables
        

    def get_driver(self, driver):
        can = self.get_driver_candidates()
        if driver in can:
            print 'Loading driver %s...' % driver
            if driver in self.hotplug:
                r_path = os.path.join(PATH_DRIVERS, 'hotplug' , driver + '.py')
            else:
                r_path = os.path.join(PATH_DRIVERS, driver + '.py')
            abs_path = os.path.abspath(r_path)
            f = None
            try:
                f = imp.load_source(driver, abs_path)
            except:
                print 'Cannot load %s' % driver, abs_path
            if f and hasattr(f, 'FUNCTIONS'):
                self.drivers_loaded[driver] = f.FUNCTIONS
                for b in self.bb:
                    for d in b.devices.values():
                        if d.name == driver:
                            d.add_functions(f.FUNCTIONS)
            else:
                print 'Driver not have FUNCTIONS'
        else:
            print 'driver not found' 


    def call_aux(self, board, modulename, number, function, params):

        device = board.devices[number]
        if not(device.has_function(function)):
            f = self.drivers_loaded[modulename]
            device.add_functions(f)

        return device.call_function(function, params)

    def callModule(self, modulename, board_number, number, function, params = []):

        if True:
        #try:
            if not(modulename in self.drivers_loaded):
                self.get_driver(modulename)

            board = self.bb[board_number]

            if not(number == None) and board.devices.has_key(number) and (board.devices[number].name == modulename):

                return self.call_aux(board, modulename, number, function, params)

            else:
                #mods = self.get_modules_list()
                if modulename in self.openables:
                    if not(modulename in self.openables_loaded[board]):
                        print 'abro', modulename
                        self.openables_loaded[board].append(modulename)
                        dev = Device(board, modulename, None)
                        h = dev.module_open()
                        dev.handler = h
                 
                        f = self.drivers_loaded[modulename]
                        dev.add_functions(f)
                        number = h
                        board.add_device(number, dev)
                    else:
                        number = board.get_device_handler(modulename)

                    if number == ERROR:
                        return ERROR
                    #print 'numero2', number
                    return self.call_aux(board, modulename, number, function, params)
                else:
                    print 'no open and no openable'
                    return -1
        """except Exception, err:
            print 'error call module', err"""


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

        for b in self.bb:
            info = ERROR
            try:
                info = b.get_info()
            except:
                print 'error refresh getinfo'

            if info == ERROR:
                self.openables_loaded[b] = []
                self.openables_loaded.pop(b)
                try:
                    b.close_device()
                except:
                    pass

        #self.find_butias()
        
        self.get_modules_list()

    def close(self):
        for b in self.bb:
            try:
                b.close_baseboard()
            except:
                print 'error close baseboard'
        self.bb = []

    def isPresent(self, module_name):
        module_list = self.get_modules_list()
        return (module_name in module_list)

    def loopBack(self, data):
        pass

    ################################ Movement calls ################################

    def set2MotorSpeed(self, leftSense = 0, leftSpeed = 0, rightSense = 0, rightSpeed = 0):
        msg = [int(leftSense), int(leftSpeed / 256.0), leftSpeed % 256, int(rightSense), int(rightSpeed / 256.0) , rightSpeed % 256]
        return self.callModule('motors', 0, None, 'setvel2mtr', msg)
     
    def setMotorSpeed(self, idMotor = 0, sense = 0, speed = 0):
        msg = [idMotor, sense, int(speed / 256.0), speed % 256]
        return self.callModule('motors', 0, None, 'setvelmtr', msg)

    ################################ Sensors calls ################################
     
    def getBatteryCharge(self):
        return self.callModule('butia', 0, None, 'get_volt')

    def getVersion(self):
        return self.callModule('butia', 0, None, 'read_ver')

    def getButton(self, number, board):
        return self.callModule('button', board, number, 'getValue')
    
    def getAmbientLight(self, number, board):
        return self.callModule('light', board, number, 'getValue')

    def getDistance(self, number, board):
        return self.callModule('distanc', board, number, 'getValue')

    def getGrayScale(self, number, board):
        return self.callModule('grey', board, number, 'getValue')

    def getResistance(self, number, board):
        vcc = 65535
        raw = self.callModule('res', board, number, 'getValue')
        if not(raw == -1):
            return raw * 6800 / (vcc - raw)
        return raw

    def getVoltaje(self, number, board):
        vcc = 65535
        raw = self.callModule('volt', board, number, 'getValue')
        if not(raw == -1):
            return raw * 5 / vcc
        return raw

    ################################ Extras ################################

    def setHacks(self, h1, h2, h3, h4, board):
        msg = [h1, h2, h3, h4]
        return self.callModule('hacks', board, None, 'set4pin', msg)


