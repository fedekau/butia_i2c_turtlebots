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

    def __init__(self):
        self.debug = True
        self.hotplug = []
        self.openables = []
        self.drivers_loaded = {}
        self.bb = []
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
        modules = []
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
                    module_type = b.get_handler_type(m)
                    module_name = listi[module_type]
                    if n_boards > 1:
                        complete_name = module_name + '@' + str(i) + ':' +  str(m)
                    else:
                        complete_name = module_name + ':' +  str(m)

                    if self.debug:
                        print '=====module', module_name, (8 - len(module_name)) * ' ', complete_name

                    if not(module_name == 'port'):

                        if normal:
                            modules.append(complete_name)
                        else:
                            modules.append((str(m), module_name, str(i)))

                        if module_name in self.openables:
                            b.add_openable_loaded(module_name)

                        d = Device(b, module_name, m)
                        if self.drivers_loaded.has_key(module_name):
                            d.add_functions(self.drivers_loaded[module_name])
                        b.add_device(m, d)
       
            except Exception, err:
                if self.debug:
                    print 'error module list', err

        return modules

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

        #print 'llega', modulename, board_number, number, function, params

        try:

            if board_number < self.get_butia_count():
                board = self.bb[board_number]

                if board.devices.has_key(number) and (board.devices[number].name == modulename):

                    return board.devices[number].call_function(function, params)

                else:
                    if modulename in self.openables:
                        if not(modulename in board.get_openables_loaded()):
                            board.add_openable_loaded(modulename)
                            dev = Device(board, modulename, None)
                            number = dev.module_open()
                            dev.add_functions(self.drivers_loaded[modulename])
                            board.add_device(number, dev)
                        else:
                            number = board.get_device_handler(modulename)

                        return board.devices[number].call_function(function, params)

                    else:
                        if self.debug:
                            print 'no open and no openable'
                        return ERROR
            else:
                if self.debug:
                    print 'no board number %s' % board_number
                return ERROR

        except Exception, err:
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
        return self.callModule('lback', board, 0, 'send', data)

    ################################ Movement calls ################################

    def set2MotorSpeed(self, leftSense = 0, leftSpeed = 0, rightSense = 0, rightSpeed = 0, board = 0):
        msg = [int(leftSense), int(leftSpeed / 256.0), leftSpeed % 256, int(rightSense), int(rightSpeed / 256.0) , rightSpeed % 256]
        return self.callModule('motors', board, 0, 'setvel2mtr', msg)
     
    def setMotorSpeed(self, idMotor = 0, sense = 0, speed = 0):
        msg = [idMotor, sense, int(speed / 256.0), speed % 256]
        return self.callModule('motors', 0, 0, 'setvelmtr', msg)

    ################################ Sensors calls ################################
     
    def getBatteryCharge(self, board=0):
        return self.callModule('butia', board, 0, 'get_volt')

    def getVersion(self, board=0):
        return self.callModule('butia', board, 0, 'read_ver')

    def getButton(self, number, board=0):
        return self.callModule('button', board, number, 'getValue')
    
    def getAmbientLight(self, number, board=0):
        return self.callModule('light', board, number, 'getValue')

    def getDistance(self, number, board=0):
        return self.callModule('distanc', board, number, 'getValue')

    def getGrayScale(self, number, board=0):
        return self.callModule('grey', board, number, 'getValue')

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
        return self.callModule('led', board, number, 'turn', str(on_off))

    ################################ Extras ################################

    def modeHack(self, pin, mode, board = 0):
        msg = str(pin) + ' ' + str(mode)
        return self.callModule('hackp', board, 'setMode', msg)

    def setHack(self, pin, value, board = 0):
        msg = str(pin) + ' ' + str(value)
        return self.callModule('hackp', board, 'write', msg)

    def getHack(self, pin, board = 0):
        pin = str(pin)
        return self.callModule('hackp', board, 'read', pin)

