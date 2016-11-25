#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Federico Kauffman <kauffman.federico@gmail.com>
# Maximiliano Kotvinsky <maxikotvi@gmail.com>
# Andrés Vasilev <andresvasilev@gmail.com>
#
# MINA/INCO/UDELAR
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import os
import sys
import types

sys.path.append('/usr/share/sugar/activities/TurtleBots.activity/plugins/butia')
from pybot import pybot_client

from gettext import gettext as _
from plugins.plugin import Plugin
from TurtleArt.tapalette import make_palette
from TurtleArt.taprimitive import Primitive, ArgSlot, ConstantArg, or_
from TurtleArt.tatype import TYPE_INT, TYPE_NUMBER, TYPE_COLOR, TYPE_STRING
from TurtleArt.taconstants import CONSTANTS, MACROS

class I2c(Plugin):

	def __init__(self, parent):
		Plugin.__init__(self)
		self.tw = parent
		self.butia = pybot_client.robot(auto_connect=True)
		self.pause = 0

	
	def setPause(self):
		self.pause = True

	def unsetPause(self):
		self.pause = False

	def getPause(self):
		return self.pause

	def setup(self):

		palette = make_palette('i2c',
					colors=["#FF6060", "#A06060"],
					help_string=_('Palette of i2c'))

		palette.add_block('openI2C',
					style='basic-style',
					label=_('openI2C'),
					value_block=True,
					help_string=_('opens an i2c connection'),
					prim_name='openI2C')

		self.tw.lc.def_prim('openI2C', 0,
			Primitive(self.openI2C))


		palette.add_block('startI2C',
					style='basic-style',
					label=_('startI2C'),
					value_block=True,
					help_string=_('starts an i2c connection'),
					prim_name='startI2C')

		self.tw.lc.def_prim('startI2C', 0,
			Primitive(self.startI2C))


		palette.add_block('stop',
					style='basic-style',
					label=_('stopI2C'),
					value_block=True,
					help_string=_('stops an i2c connection'),
					prim_name='stopI2C')

		self.tw.lc.def_prim('stopI2C', 0,
			Primitive(self.stopI2C))


		palette.add_block('closeI2C',
					style='basic-style',
					label=_('closeI2C'),
					value_block=True,
					help_string=_('closes an i2c connection'),
					prim_name='closeI2C')

		self.tw.lc.def_prim('closeI2C', 0,
			Primitive(self.closeI2C))


		palette.add_block('writeI2C',
					style='basic-style-1arg',
					label=[_('writeI2C')],
					default=1,
					help_string=_('writeI2C'),
					prim_name='writeI2C')

		self.tw.lc.def_prim('writeI2C', 1,
			Primitive(self.writeI2C, arg_descs=[ArgSlot(TYPE_INT)]))


		palette.add_block('ackI2C',
					style='basic-style',
					label=_('ackI2C'),
					value_block=True,
					help_string=_('ackI2C'),
					prim_name='ackI2C')

		self.tw.lc.def_prim('ackI2C', 0,
			Primitive(self.ackI2C))


		palette.add_block('notAckI2C',
					style='basic-style',
					label=_('notAckI2C'),
					value_block=True,
					help_string=_('notAckI2C'),
					prim_name='notAckI2C')

		self.tw.lc.def_prim('notAckI2C', 0,
			Primitive(self.notAckI2C))


		palette.add_block('readI2C',
					style='box-style',
					label=_('readI2C'),
					help_string=_('readI2C'),
					prim_name='readI2C')

		self.tw.lc.def_prim('readI2C', 0,
			Primitive(self.readI2C, TYPE_NUMBER))



	############################# Turtle calls ################################

	def start(self):
		pass

	def stop(self):
		pass

	def quit(self):
		pass

	################################# Primitives ##############################

	def openI2C(self, port='0', board='0'):
		self.butia.openI2C(port, board)


	def startI2C(self, port='0', board='0'):
		self.butia.startI2C(port, board)


	def stopI2C(self, port='0', board='0'):
		self.butia.stopI2C(port, board)


	def closeI2C(self, port='0', board='0'):
		self.butia.closeI2C(port, board)


	def writeI2C(self, value='', port='0', board='0'):
		self.butia.writeI2C(value, port, board)


	def readI2C(self, port='0', board='0'):
		return self.butia.readI2C(port, board)


	def ackI2C(self, port='0', board='0'):
		self.butia.ackI2C(port, board)


	def notAckI2C(self, port='0', board='0'):
		self.butia.notAckI2C(port, board)

		
