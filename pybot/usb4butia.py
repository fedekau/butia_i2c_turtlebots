#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# USB4Butia main
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


import os
import imp
import com_usb
from baseboard import Baseboard
from device import Device

ERROR = -1

class USB4Butia():

    def __init__(self, debug=False):
        self.debug = debug
        self.hotplug = []
        self.openables = []
        self.drivers_loaded = {}
        self.bb = []
        self.modules = []
        self.get_all_drivers()
        self.find_butias()

    def get_butia_count(self):
        return len(self.bb)

    def find_butias(self, get_modules=True):
        devices = com_usb.find()
        for dev in devices:
            b = Baseboard(dev)
            try:
                b.open_baseboard()
                self.bb.append(b)
            except:
                if self.debug:
                    print 'error open baseboard'
        if get_modules:
            self.get_modules_list()

    def get_modules_list(self, normal=True):
        self.modules = []
        n_boards = self.get_butia_count()

        if self.debug:
            print '=Listing Devices'

        for i, b in enumerate(self.bb):
            try:
                listi = b.get_listi()
                s = b.get_handler_size()

                if self.debug:
                    print '===board', i

                for m in range(0, s + 1):
                    module_name = listi[b.get_handler_type(m)]
                    if n_boards > 1:
                        complete_name = module_name + '@' + str(i) + ':' +  str(m)
                    else:
                        complete_name = module_name + ':' +  str(m)

                    if self.debug:
                        print '=====module', module_name, (8 - len(module_name)) * ' ', complete_name

                    if not(module_name == 'port'):

                        if normal:
                            self.modules.append(complete_name)
                        else:
                            self.modules.append((str(m), module_name, str(i)))

                        if not(b.devices.has_key(m) and (b.devices[m].name == module_name)):
                            d = Device(b, module_name, m)
                            d.add_functions(self.drivers_loaded[module_name])
                            b.add_device(m, d)

                            if module_name in self.openables:
                                b.add_openable_loaded(module_name)
                    else:
                        if b.devices.has_key(m):
                            b.devices.pop(m)

            except Exception, err:
                if self.debug:
                    print 'error module list', err

        return self.modules

    def get_all_drivers(self):
        # current folder
        path_drivers = os.path.join(os.path.dirname(__file__), 'drivers')
        if self.debug:
            print 'Searching drivers in: ', path_drivers
        # normal drivers
        tmp = os.listdir(path_drivers)
        tmp.sort()
        for d in tmp:
            if d.endswith('.py'):
                name = d.replace('.py', '')
                self.openables.append(name)
                self.get_driver(path_drivers, name)
        # hotplug drivers
        path = os.path.join(path_drivers, 'hotplug')
        tmp = os.listdir(path)
        tmp.sort()
        for d in tmp:
            if d.endswith('.py'):
                name = d.replace('.py', '')
                self.hotplug.append(name)
                self.get_driver(path, name)

    def get_driver(self, path, driver):
        if self.debug:
            print 'Loading driver %s...' % driver
        abs_path = os.path.abspath(os.path.join(path, driver + '.py'))
        f = None
        try:
            f = imp.load_source(driver, abs_path)
        except:
            if self.debug:
                print 'Cannot load %s' % driver, abs_path
        if f and hasattr(f, 'FUNCTIONS'):
            self.drivers_loaded[driver] = f.FUNCTIONS
        else:
            if self.debug:
                print 'Driver not have FUNCTIONS'

    def callModule(self, modulename, board_number, number, function, params = []):
        try:
            board = self.bb[board_number]
            if board.devices.has_key(number) and (board.devices[number].name == modulename):
                return board.devices[number].call_function(function, params)
            else:
                if modulename in self.openables:
                    if modulename in board.get_openables_loaded():
                        number = board.get_device_handler(modulename)
                    else:
                        board.add_openable_loaded(modulename)
                        dev = Device(board, modulename)
                        number = dev.module_open()
                        dev.add_functions(self.drivers_loaded[modulename])
                        board.add_device(number, dev)
                    return board.devices[number].call_function(function, params)
                else:
                    if self.debug:
                        print 'no open and no openable'
                    return ERROR
        except Exception, err:
            if self.debug:
                print 'error call module', err
            return ERROR

    def reconnect(self):
        pass

    def refresh(self):
        if self.bb == []:
            self.find_butias(False)
        else:
            for b in self.bb:
                info = ERROR
                try:
                    info = b.get_info()
                except:
                    if self.debug:
                        print 'error refresh getinfo'

                if info == ERROR:
                    self.bb.remove(b)
                    try:
                        b.close_baseboard()
                    except:
                        pass

    def close(self):
        for b in self.bb:
            try:
                b.close_baseboard()
            except:
                if self.debug:
                    print 'error in close baseboard'
        self.bb = []

    def isPresent(self, module_name):
        module_list = self.get_modules_list()
        return (module_name in module_list)

    def loopBack(self, data, board=0):
        return self.callModule('lback', board, 0, 'send', [data])

    ################################ Movement calls ################################

    def set2MotorSpeed(self, leftSense = 0, leftSpeed = 0, rightSense = 0, rightSpeed = 0, board = 0):
        msg = [int(leftSense), int(leftSpeed / 256.0), leftSpeed % 256, int(rightSense), int(rightSpeed / 256.0) , rightSpeed % 256]
        return self.callModule('motors', board, 0, 'setvel2mtr', msg)
     
    def setMotorSpeed(self, idMotor = 0, sense = 0, speed = 0, board = 0):
        msg = [idMotor, sense, int(speed / 256.0), speed % 256]
        return self.callModule('motors', board, 0, 'setvelmtr', msg)

    ############################### General calls ###############################
     
    def getBatteryCharge(self, board=0):
        return self.callModule('butia', board, 0, 'get_volt')

    def getVersion(self, board=0):
        return self.callModule('butia', board, 0, 'read_ver')

    def getFirmwareVersion(self, board=0):
        return self.callModule('admin', board, 0, 'getVersion')

    ############################### Sensors calls ###############################

    def getButton(self, number, board=0):
        res = self.callModule('button', board, number, 'getValue')
        if res != ERROR:
            return (1 - res)
        else:
            return res
    
    def getAmbientLight(self, number, board=0):
        m = 65535
        res = self.callModule('light', board, number, 'getValue')
        if res != ERROR:
            return (m - res)
        else:
            return res

    def getDistance(self, number, board=0):
        return self.callModule('distanc', board, number, 'getValue')

    def getGrayScale(self, number, board=0):
        return self.callModule('grey', board, number, 'getValue')

    def getTemperature(self, number, board=0):
        return self.callModule('temp', board, number, 'getValue')

    def getResistance(self, number, board=0):
        vcc = 65535
        raw = self.callModule('res', board, number, 'getValue')
        if not(raw == ERROR):
            return raw * 6800 / (vcc - raw)
        return raw

    def getVoltage(self, number, board=0):
        vcc = 65535
        raw = self.callModule('volt', board, number, 'getValue')
        if not(raw == ERROR):
            return raw * 5 / vcc
        return raw

    def setLed(self, on_off, number, board):
        return self.callModule('led', board, number, 'turn', [int(on_off)])

    ################################ Extras ################################

    def modeHack(self, pin, mode, board = 0):
        msg = [int(pin), int(mode)]
        return self.callModule('hackp', board, 0, 'setMode', msg)

    def setHack(self, pin, value, board = 0):
        msg = [int(pin), int(value)]
        return self.callModule('hackp', board, 0, 'write', msg)

    def getHack(self, pin, board = 0):
        return self.callModule('hackp', board, 0, 'read', [int(pin)])

