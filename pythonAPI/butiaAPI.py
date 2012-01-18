# -*- coding: utf-8 -*-
# ButiaAPI
# Copyright (c) 2009, 2010, 2011, 2012 Butiá Team butia@fing.edu.uy 
# Butia is a free open plataform for robotics projects
# www.fing.edu.uy/inco/proyectos/butia
# Facultad de Ingenieria - Universidad de la República - Uruguay
#
# Implementa una capa de abstraccion para la comunicacion con el bobot-server
# version 3_0 //reorganiza el codigo pa mas legible y menos codigo repetido
# version 2_0 //agrega funcionalidades para manejar nuevos drivers 
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

import socket
import string
import math 

BOBOT_ADDRESS = 'localhost'
BOBOT_PORT = '2009'
	
class robot:
	client = None
	fclient = None

	# init the robot class
	def __init__(self):
		self.reconnect(BOBOT_ADDRESS, BOBOT_PORT)

	# connect o reconnect the bobot
	def reconnect(self):
		self.close()
		try:
			self.client = socket.socket()
			self.client.connect((BOBOT_ADDRESS, BOBOT_PORT))  
			self.fclient = self.client.makefile()
			msg = 'INIT\n'
			self.client.send(msg) #bobot server instance is running, but we have to check for new or remove hardware
			self.fclient.readline()
		except:
			return -1
		return 0

	# close the comunication with the lubot
	def close(self):
		try:
			if self.fclient != None:
				self.fclient.close()
				self.fclient = None
			if self.client != None:
				self.client.close()
				self.client = None
		except:
			return -1
		return 0

	#######################################################################
	### Operations to the principal module
	#######################################################################

	# return a string list om modules istar modulos: devuelve la lista de los modulos disponibles en el firmware de la placa
	def moduleList(self):
		ret = -1
		msg = 'LIST\n'
		try:
			self.client.send(msg)
			ret = self.fclient.readline()
		except:	
			return -1
		ret = ret[:len(ret) -1]
		return ret

	# open the module 'moduloname'
	def moduleOpen(self, moduloname):
		ret = -1
		msg = 'OPEN ' + moduloname  + '\n'
		try:
			self.client.send(msg)
			ret = self.fclient.readline()
		except:
			return -1
		ret = ret[:len(ret) -1]
		return ret

	# call the module 'modulename'
	def moduleCall(self, modulename, function , params = ''):
		ret = -1
		msg = 'CALL ' + modulename + ' ' + function
		if params != '' :
			msg += ' ' + params
		msg += '\n'
		try:
			self.client.send(msg)
			ret = self.fclient.readline()
		except:
			return -1
		ret = ret[:len(ret) -1]
		return ret

	#######################################################################
	### Useful functions 
	#######################################################################

	# returns if the module_name is present
	def isPresent(self, module_name):
		module_list = self.get_modules_list()
		return (module_name in module_list)

	# returns a list of modules
	def get_modules_list(self):
		ret = self.listarModulos()
		if ret == '':
			return []
		return string.split(ret,',')

	# loopBack: send a message to butia and wait to recibe the same
	def loopBack(self, data):
		ret = self.callModule('lback', 'send', data)
		if ret == -1 :
			return -1
		return self.callModule('lback', 'read')

	#######################################################################
	### Operations for motores.lua driver
	#######################################################################

	def set2MotorSpeed(self, leftSense = '0', leftSpeed = '0', rightSense = '0', rightSpeed = '0'):
		msg = leftSense + ' ' + leftSpeed + ' ' + rightSense + ' ' + rightSpeed
		return self.callModule('motores', 'setvel2mtr', msg)
	 
	def setMotorSpeed(self, idMotor = '0', sense = '0', speed = '0'):
		msg = idMotor + ' ' + sense + ' ' + speed
		return self.callModule('motores', 'setvelmtr', msg)

	#######################################################################
        ### Operations for butia.lua driver
	#######################################################################

	def ping(self):
		return self.callModule('placa', 'ping')

	# returns the approximate charge of the battery	
	def getBatteryCharge(self):
		return self.callModule('butia', 'get_volt')
	 
	# returns the firmware version 
	def getVersion(self):
		return self.callModule('butia', 'read_ver')
        
        # set de motor idMotor on determinate angle
	def setPosition(self, idMotor = 0, angle = 0):
		msg = str(idMotor) + ' ' + str(angle)
		return self.callModule('placa', 'setPosicion' , msg )
	
        # return the value of button: 1 if pressed, 0 otherwise
	def getButton(self, number=''):
		return self.callModule('boton' + number, 'getBoton')
	
        # return the value en ambient light sensor
	def getAmbientLight(self, number=''):
		return self.callModule('luz' + number, 'getLuz')

        # return the value of the distance sensor
	def getDistance(self, number=''):
		return self.callModule('dist' + number, 'getDistancia')
	
        # return the value of the grayscale sensor
	def getGrayScale(self, number=''):
		return self.callModule('grises' + number, 'getLevel')

        # return the value of the temperature sensor
	def getTemperature(self, number=''):
		return self.callModule('temp' + number, 'getTemp')

        # return the value of the vibration sensor
	def getVibration(self, number=''):
		return self.callModule('vibra' + number, 'getVibra')

        # return the value of the tilt sensor
	def getTilt(self, number=''):
		return self.callModule('tilt' + number, 'getTilt')

        # return the value of the magnetic induction sensor
	def getMagneticInduction(self, number=''):
		return self.callModule('magnet' + number, 'getCampo')

        # set the led intensity
	def setLed(self, number= '', nivel = 255):
		return self.callModule('led' + number, 'setLight', str(math.trunc(nivel)))

