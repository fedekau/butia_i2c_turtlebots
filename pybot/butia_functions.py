#! /usr/bin/env python
# -*- coding: utf-8 -*-


class functions():

    def __init__(self):
        pass

    def isPresent(self, module_name):
        """
        Check if module: module_name is present
        """
        module_list = self.get_modules_list()
        return (module_name in module_list)

    def loopBack(self, data, board=0):
        """
        LoopBack command: send data to the board and get the result. If all is ok
        the return must be exactly of the data parameter
        """
        return self.callModule('lback', board, 0, 'send', [data])

    ############################## Movement calls ##############################

    def set2MotorSpeed(self, leftSense = 0, leftSpeed = 0, rightSense = 0, rightSpeed = 0, board = 0):
        """
        Set the speed of 2 motors. The sense is 0 or 1, and the speed is
        between 0 and 1023
        """
        msg = [int(leftSense), int(leftSpeed), int(rightSense), int(rightSpeed)]
        return self.callModule('motors', board, 0, 'setvel2mtr', msg)
     
    def setMotorSpeed(self, idMotor = 0, sense = 0, speed = 0, board = 0):
        """
        Set the speed of one motor. idMotor = 0 for left motor and 1 for the
        right motor. The sense is 0 or 1, and the speed is between 0 and 1023
        """
        msg = [idMotor, sense, int(speed)]
        return self.callModule('motors', board, 0, 'setvelmtr', msg)


    ##################### Operations for ax.lua driver #########################

    def wheel_mode(self, idMotor = '0'):
        msg = idMotor
        return self.callModule('ax', 'wheel_mode', msg)
     
    def joint_mode(self, idMotor = '0', min = '0', max = '1023'):
        msg = idMotor + ' ' + min + ' ' + max
        return self.callModule('ax', 'joint_mode', msg)

	def set_speed(self, idMotor = '0', speed = '0'):
		msg = idMotor + ' ' + speed 
        return self.callModule('ax', 'set_speed', msg)

    def set_position(self, idMotor = '0', pos = '0'):
        msg = idMotor + ' ' + pos
        return self.callModule('ax', 'set_position', msg)

    def get_position(self, idMotor = '0'):
        msg = idMotor
        return self.callModule('ax', 'get_position', msg)

    def ping(self, board=0):
        return self.callModule('placa', board, 0, 'ping')

    ############################### General calls ###############################
     
    def getBatteryCharge(self, board=0):
        """
        Gets the battery level charge
        """
        return self.callModule('butia', board, 0, 'get_volt')

    def getVersion(self, board=0):
        """
        Gets the version of Butiá module. 22 for new version
        """
        return self.callModule('butia', board, 0, 'read_ver')

    def getFirmwareVersion(self, board=0):
        """
        Gets the version of the Firmware
        """
        return self.callModule('admin', board, 0, 'getVersion')

    ############################### Sensors calls ###############################

    def getButton(self, number, board=0):
        """
        Gets the value of the button connected in port: number
        """
        return self.callModule('button', board, number, 'getValue')
    
    def getLight(self, number, board=0):
        """
        Gets the value of the light sensor connected in port: number
        """
        return self.callModule('light', board, number, 'getValue')

    def getDistance(self, number, board=0):
        """
        Gets the value of the distance sensor connected in port: number
        """
        return self.callModule('distanc', board, number, 'getValue')

    def getGray(self, number, board=0):
        """
        Gets the value of the gray sensor connected in port: number
        """
        return self.callModule('grey', board, number, 'getValue')

    def getTemperature(self, number, board=0):
        """
        Gets the value of the temperature sensor connected in port: number
        """
        return self.callModule('temp', board, number, 'getValue')

    def getResistance(self, number, board=0):
        """
        Gets the value of the resistance sensor connected in port: number
        """
        return self.callModule('res', board, number, 'getValue')

    def getVoltage(self, number, board=0):
        """
        Gets the value of the voltage sensor connected in port: number
        """
        return self.callModule('volt', board, number, 'getValue')

    def setLed(self, number, on_off, board=0):
        """
        Sets on or off the LED connected in port: number (0 is off, 1 is on)
        """
        return self.callModule('led', board, number, 'turn', [int(on_off)])

    ################################ Extras ################################

    def modeHack(self, pin, mode, board = 0):
        """
        Sets the mode of hack pin. If mode 0 = input, mode 1 = output
        """
        msg = [int(pin), int(mode)]
        return self.callModule('hackp', board, 0, 'setMode', msg)

    def setHack(self, pin, value, board = 0):
        """
        Sets the value of hack pin configured as output. Value is 0 or 1
        """
        msg = [int(pin), int(value)]
        return self.callModule('hackp', board, 0, 'write', msg)

    def getHack(self, pin, board = 0):
        """
        Gets the value of hack pin configured as input. Returns 0 or 1
        """
        return self.callModule('hackp', board, 0, 'read', [int(pin)])

