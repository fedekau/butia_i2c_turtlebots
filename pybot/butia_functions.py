#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Abstract class with common functions
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


class functions:

    def isPresent(self, module_name):
        """
        Check if module: module_name is present
        """
        module_list = self.get_modules_list()
        return (module_name in module_list)

    def loopBack(self, data, board='0'):
        """
        LoopBack command: send data to the board and get the result. If all is ok
        the return must be exactly of the data parameter
        """
        return self.callModule('lback', str(board), '0', 'send', str(data))

    ############################## Movement calls ##############################

    def set2MotorSpeed(self, leftSense='0', leftSpeed='0', rightSense='0', rightSpeed='0', board='0'):
        """
        Set the speed of 2 motors. The sense is 0 or 1, and the speed is
        between 0 and 1023
        """
        msg = str(leftSense) + ' ' + str(leftSpeed) + ' ' + str(rightSense)
        msg = msg + ' ' +  str(rightSpeed)
        return self.callModule('motors', str(board), '0', 'setvel2mtr', msg)
     
    def setMotorSpeed(self, idMotor='0', sense='0', speed='0', board='0'):
        """
        Set the speed of one motor. idMotor = 0 for left motor and 1 for the
        right motor. The sense is 0 or 1, and the speed is between 0 and 1023
        """
        msg = str(idMotor) + ' ' + str(sense) + ' ' + str(speed)
        return self.callModule('motors', str(board), '0', 'setvelmtr', msg)


    ##################### Operations for ax.lua driver #########################

    def wheel_mode(self, idMotor='0'):
        msg = str(idMotor)
        return self.callModule('ax', 'wheel_mode', msg)
     
    def joint_mode(self, idMotor='0', _min='0', _max='1023'):
        msg = str(idMotor) + ' ' + str(_min) + ' ' + str(_max)
        return self.callModule('ax', 'joint_mode', msg)

	def set_speed(self, idMotor='0', speed='0'):
		msg = str(idMotor) + ' ' + str(speed) 
        return self.callModule('ax', 'set_speed', msg)

    def set_position(self, idMotor='0', pos='0'):
        msg = str(idMotor) + ' ' + str(pos)
        return self.callModule('ax', 'set_position', msg)

    def get_position(self, idMotor='0'):
        msg = str(idMotor)
        return self.callModule('ax', 'get_position', msg)

    def ping(self, board='0'):
        return self.callModule('placa', str(board), '0', 'ping')

    ############################### General calls ###############################
     
    def getBatteryCharge(self, board='0'):
        """
        Gets the battery level charge
        """
        return self.callModule('butia', str(board), '0', 'getVolt')

    def getVersion(self, board='0'):
        """
        Gets the version of Butiá module. 22 for new version
        """
        return self.callModule('butia', str(board), '0', 'getVersion')

    def getFirmwareVersion(self, board='0'):
        """
        Gets the version of the Firmware
        """
        return self.callModule('admin', str(board), '0', 'getVersion')

    ############################### Sensors calls ###############################

    def getButton(self, number, board='0'):
        """
        Gets the value of the button connected in port: number
        """
        return self.callModule('button', str(board), str(number), 'getValue')
    
    def getLight(self, number, board='0'):
        """
        Gets the value of the light sensor connected in port: number
        """
        return self.callModule('light', str(board), str(number), 'getValue')

    def getDistance(self, number, board='0'):
        """
        Gets the value of the distance sensor connected in port: number
        """
        return self.callModule('distanc', str(board), str(number), 'getValue')

    def getGray(self, number, board='0'):
        """
        Gets the value of the gray sensor connected in port: number
        """
        return self.callModule('grey', str(board), str(number), 'getValue')

    def getTemperature(self, number, board='0'):
        """
        Gets the value of the temperature sensor connected in port: number
        """
        return self.callModule('temp', str(board), str(number), 'getValue')

    def getResistance(self, number, board='0'):
        """
        Gets the value of the resistance sensor connected in port: number
        """
        return self.callModule('res', str(board), str(number), 'getValue')

    def getVoltage(self, number, board='0'):
        """
        Gets the value of the voltage sensor connected in port: number
        """
        return self.callModule('volt', str(board), str(number), 'getValue')

    def setLed(self, number, on_off, board='0'):
        """
        Sets on or off the LED connected in port: number (0 is off, 1 is on)
        """
        return self.callModule('led', str(board), str(number), 'turn', str(on_off))

    ################################ Extras ################################

    def modeHack(self, pin, mode, board='0'):
        """
        Sets the mode of hack pin. If mode 0 = input, mode 1 = output
        """
        msg = str(pin) + ' ' + str(mode)
        return self.callModule('hackp', str(board), '0', 'setMode', msg)

    def setHack(self, pin, value, board='0'):
        """
        Sets the value of hack pin configured as output. Value is 0 or 1
        """
        msg = str(pin) + ' ' + str(value)
        return self.callModule('hackp', str(board), '0', 'write', msg)

    def getHack(self, pin, board='0'):
        """
        Gets the value of hack pin configured as input. Returns 0 or 1
        """
        return self.callModule('hackp', str(board), '0', 'read', str(pin))


