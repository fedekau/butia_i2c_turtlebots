#! /usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright (c) 2011 Butiá Team butia@fing.edu.uy 
# Butia is a free open plataform for robotics projects
# www.fing.edu.uy/inco/proyectos/butia
# Universidad de la República del Uruguay
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

import gobject
import butiaAPI
import time
import math
import os
import threading
import re
import subprocess
import commands

from TurtleArt.tapalette import special_block_colors
from TurtleArt.tapalette import palette_name_to_index
from TurtleArt.tapalette import palette_blocks
from TurtleArt.tapalette import make_palette
from TurtleArt.talogo import primitive_dictionary
from TurtleArt.taconstants import BOX_COLORS
from TurtleArt.tautils import debug_output

from plugins.plugin import Plugin

from gettext import gettext as _

#constants definitions
ERROR_SENSOR_READ = -1   # default return value in case of error when reading a sensor
WAIT_FOR_BOBOT = 4   # waiting trys for bobot-server (the butia robot lua server)
MAX_SPEED = 1023   # max velocity for AX-12 - 10 bits -
MAX_SENSOR_PER_TYPE = 4
COLOR_NOTPRESENT = ["#A0A0A0","#808080"] 
COLOR_PRESENT = ["#00FF00","#008000"] #FIXME change for another tone of gray to avoid confusion with some similar blocks or the turtle
WHEELBASE = 28.00

#Dictionary for help string asociated to modules used for automatic generation of block instances
modules_help = {} 
modules_help['led'] = _("adjust LED intensity between 0 and 255")
modules_help['grayscale'] = _("returns the object gray level as a number between 0 and 1023")
modules_help['button'] = _("returns 1 when the button is press and 0 otherwise")
modules_help['ambientlight'] = _("returns the ambient light level as a number between 0 and 1023")
modules_help['temperature'] = _("returns the ambient temperature as a number between 0 and 255")
modules_help['distance'] = _("returns the distance from the object in front of the sensor as a number between 0 and 255")
modules_help['tilt'] = _("returns 0 or 1 depending on the sensor inclination")
modules_help['magneticinduction'] = _("returns 1 when the sensors detects a magnetic field, 0 otherwise")
modules_help['vibration'] = _("switches from 0 to 1, the frequency depends on the vibration")


#Dictionary for translating block name to module name used for automatic generation of block instances

modules_name_from_device_id = {} 
modules_name_from_device_id['led'] = 'led'
modules_name_from_device_id['button'] = 'boton'
modules_name_from_device_id['grayscale'] = 'grises'
modules_name_from_device_id['ambientlight'] = 'luz'
modules_name_from_device_id['temperature'] = 'temp'
modules_name_from_device_id['distance'] = 'dist'
modules_name_from_device_id['tilt'] = 'tilt'
modules_name_from_device_id['magneticinduction'] = 'magnet'
modules_name_from_device_id['vibration'] = 'vibra'

device_id_from_module_name = {} 
device_id_from_module_name['led'] = 'led'
device_id_from_module_name['boton'] = 'button'
device_id_from_module_name['grises'] = 'grayscale'
device_id_from_module_name['luz'] = 'ambientlight'
device_id_from_module_name['temp'] = 'temperature'
device_id_from_module_name['dist'] = 'distance'
device_id_from_module_name['tilt'] = 'tilt'
device_id_from_module_name['magnet'] = 'magneticinduction'
device_id_from_module_name['vibra'] = 'vibration'

label_name_from_device_id= {} 
label_name_from_device_id['led'] = _('LED')
label_name_from_device_id['button'] = _('button')
label_name_from_device_id['grayscale'] = _('grayscale')
label_name_from_device_id['ambientlight'] = _('ambient light')
label_name_from_device_id['temperature'] = _('temperature')
label_name_from_device_id['distance'] = _('distance')
label_name_from_device_id['tilt'] = _('tilt')
label_name_from_device_id['magneticinduction'] = _('magnetic induction')
label_name_from_device_id['vibration'] = _('vibration')

#list of devices that will be checked in the refresh event
refreshable_block_list = ['ambientlight', 'grayscale', 'temperature', 'distance', 'button', 'tilt', 'magneticinduction', 'vibration', 'led' ]

refreshable_module_list = ['luz', 'grises', 'temp', 'dist', 'boton', 'tilt', 'magnet', 'vibra', 'led' ]

static_block_list = ['forwardButia', 'backwardButia', 'leftButia', 'rightButia', 'stopButia', 'speedButia', 'forwardDistance', 
              'backwardDistance', 'turnXdegree', 'LCDdisplayButia', 'batterychargeButia'] 

class Butia(Plugin):
    actualSpeed = 600
    def __init__(self, parent):
        self.tw = parent
        self.butia = None
        self.pollthread = None
        self.pollrun = False
        self.old_battery_value = 0
        self.bobot = None
        self.butia = None
        self.list_connected_device_module = []
        self.pollthread=threading.Timer(0,self.bobot_launch)
        self.pollthread.start()
        self.can_refresh = True
        self.regex = re.compile(r"""^		#Start of the string
                                (\D*?)			# name, an string  without digits, the ? mark says that it's not greedy, to avoid to consume also the "Butia" part, in case it's present
                                (\d*)				# index, a group comprised only of digits, posibly absent
                                (?:Butia)?			# an ocurrence of the "Butia" string, the first ? mark says that the group hasn't to be returned, the second that the group might or not be present 
                                $				# end of the string, this regex must match all of the input
                        """, re.X) # Verbose definition, to include comments
    

    def setup(self):
        """ Setup is called once, when the Turtle Window is created. """

        if self.butia:
            battery = self.butia.getBatteryCharge()
        else:
            battery = ERROR_SENSOR_READ

        COLOR_STATIC = self.staticBlocksColor(battery)
        COLOR_BATTERY = self.batteryColor(battery)

        palette = make_palette('butia', colors=COLOR_NOTPRESENT, help_string=_('Butia Robot'))

        #add block about movement of butia, this blocks don't allow multiple instances

        primitive_dictionary['refreshButia'] = self.refreshButia
        palette.add_block('refreshButia',  # the name of your block
                     style='basic-style',  # the block style
                     label=_('refresh Butia'),  # the label for the block
                     prim_name='refreshButia',  # code reference (see below)
                     help_string=_('force to refresh the state of the butia plugin blocks'))
        self.tw.lc.def_prim('refreshButia', 0, lambda self: primitive_dictionary['refreshButia']())
        special_block_colors['refreshButia'] = COLOR_PRESENT
        BOX_COLORS['refreshButia'] = COLOR_PRESENT

        primitive_dictionary['batterychargeButia'] = self.batterychargeButia
        palette.add_block('batterychargeButia',  # the name of your block
                     style='box-style',  # the block style
                     label=_('battery charge Butia'),  # the label for the block
                     prim_name='batterychargeButia',  # code reference (see below)
                     help_string=_('returns the battery charge as a number between 0 and 255'))
        self.tw.lc.def_prim('batterychargeButia', 0, lambda self: primitive_dictionary['batterychargeButia']())
        BOX_COLORS['batterychargeButia'] = COLOR_BATTERY

        primitive_dictionary['speedButia'] = self.speedButia
        palette.add_block('speedButia',  # the name of your block
                     style='basic-style-1arg',  # the block style
                     label=_('speed Butia'),  # the label for the block
                     prim_name='speedButia',  # code reference (see below)
                     default=[600],
                     help_string=_('set the speed of the Butia motors as a value between 0 and 1023, passed by an argument'))
        self.tw.lc.def_prim('speedButia', 1, lambda self, x: primitive_dictionary['speedButia'](x))
        BOX_COLORS['speedButia'] = COLOR_STATIC
        
        primitive_dictionary['forwardButia'] = self.forwardButia
        palette.add_block('forwardButia',  # the name of your block
                     style='basic-style',  # the block style
                     label=_('forward Butia'),  # the label for the block
                     prim_name='forwardButia',  # code reference (see below)
                     help_string=_('move the Butia robot forward'))
        self.tw.lc.def_prim('forwardButia', 0, lambda self: primitive_dictionary['forwardButia']())
        BOX_COLORS['forwardButia'] = COLOR_STATIC

        primitive_dictionary['forwardDistance'] = self.forwardDistance
        palette.add_block('forwardDistance',  # the name of your block
                     style='basic-style-1arg',  # the block style
                     label=_('forward Butia'),  # the label for the block
                     default=[5],  
                     prim_name='forwardDistance',  # code reference (see below)
                     help_string=_('move the Butia robot forward a predefined distance'))
        self.tw.lc.def_prim('forwardDistance', 1, lambda self, x: primitive_dictionary['forwardDistance'](x))
        BOX_COLORS['forwardDistance'] = COLOR_STATIC

        primitive_dictionary['leftButia'] = self.leftButia
        palette.add_block('leftButia',  # the name of your block
                     style='basic-style',  # the block style
                     label=_('left Butia'),  # the label for the block
                     prim_name='leftButia',  # code reference (see below)
                     help_string=_('turn the Butia robot at left'))
        self.tw.lc.def_prim('leftButia', 0, lambda self: primitive_dictionary['leftButia']())
        BOX_COLORS['leftButia'] = COLOR_STATIC
        
        primitive_dictionary['backwardButia'] = self.backwardButia
        palette.add_block('backwardButia',  # the name of your block
                     style='basic-style',  # the block style
                     label=_('backward Butia'),  # the label for the block
                     prim_name='backwardButia',  # code reference (see below)
                     help_string=_('move the Butia robot backward'))
        self.tw.lc.def_prim('backwardButia', 0, lambda self: primitive_dictionary['backwardButia']())
        BOX_COLORS['backwardButia'] = COLOR_STATIC

        primitive_dictionary['backwardDistance'] = self.backwardDistance
        palette.add_block('backwardDistance',  # the name of your block
                     style='basic-style-1arg',  # the block style
                     label=_('backward Butia'),  # the label for the block
                     default=[5],  
                     prim_name='backwardDistance',  # code reference (see below)
                     help_string=_('move the Butia robot backward a predefined distance'))
        self.tw.lc.def_prim('backwardDistance', 1, lambda self, x: primitive_dictionary['backwardDistance'](x))
        BOX_COLORS['backwardDistance'] = COLOR_STATIC

        primitive_dictionary['rightButia'] = self.rightButia
        palette.add_block('rightButia',  # the name of your block
                     style='basic-style',  # the block style
                     label=_('right Butia'),  # the label for the block
                     prim_name='rightButia',  # code reference (see below)
                     help_string=_('turn the Butia robot at right'))
        self.tw.lc.def_prim('rightButia', 0, lambda self: primitive_dictionary['rightButia']())
        BOX_COLORS['rightButia'] = COLOR_STATIC

        primitive_dictionary['turnXdegree'] = self.turnXdegree
        palette.add_block('turnXdegree',  # the name of your block
                     style='basic-style-1arg',  # the block style
                     label=_('turn Butia'),  # the label for the block
                     default=[45],  
                     prim_name='turnXdegree',  # code reference (see below)
                     help_string=_('turn the Butia robot x degrees'))
        self.tw.lc.def_prim('turnXdegree', 1, lambda self, x: primitive_dictionary['turnXdegree'](x))
        BOX_COLORS['turnXdegree'] = COLOR_STATIC

        primitive_dictionary['stopButia'] = self.stopButia
        palette.add_block('stopButia',  # the name of your block
                     style='basic-style',  # the block style
                     label=_('stop Butia'),  # the label for the block
                     prim_name='stopButia',  # code reference (see below)
                     help_string=_('stop the Butia robot'))
        self.tw.lc.def_prim('stopButia', 0, lambda self: primitive_dictionary['stopButia']())
        BOX_COLORS['stopButia'] = COLOR_STATIC

        primitive_dictionary['LCDdisplayButia'] = self.LCDdisplayButia
        palette.add_block('LCDdisplayButia',  # the name of your block
                     style='basic-style-1arg',  # the block style
                     label=_('display Butia'),  # the label for the block
                     default=[_('Hello World    Butia            ')],   
                     prim_name='LCDdisplayButia',  # code reference (see below)
                     help_string=_('print text in Butia robot 32-character ASCII display'))
        self.tw.lc.def_prim('LCDdisplayButia', 1, lambda self, x: primitive_dictionary['LCDdisplayButia'](x))
        BOX_COLORS['LCDdisplayButia'] = COLOR_STATIC


        #add every function in the code 
        primitive_dictionary['ledButia'] = self.ledButia
        primitive_dictionary['ambientlightButia'] = self.ambientlightButia
        primitive_dictionary['grayscaleButia'] = self.grayscaleButia
        primitive_dictionary['buttonButia'] = self.buttonButia
        primitive_dictionary['temperatureButia'] = self.temperatureButia
        primitive_dictionary['distanceButia'] = self.distanceButia
        primitive_dictionary['tiltButia'] = self.tiltButia
        primitive_dictionary['magneticinductionButia'] = self.magneticinductionButia
        primitive_dictionary['vibrationButia'] = self.vibrationButia

        if self.butia:
            self.list_connected_device_module = self.butia.get_modules_list()
        else:
            self.list_connected_device_module = []
        

        #generic mecanism to add sensors that allows multiple instances, depending on the number of instances connected to the 
        #physical robot the corresponding block appears in the pallete

        for i in [   ['basic-style-1arg', ['led']],
                     ['box-style', ['button', 'grayscale', 'ambientlight', 'temperature', 'distance', 'tilt', 'magneticinduction', 'vibration']]
                 ]:

            (blockstyle , listofmodules) = i
            for j in listofmodules:
                block_name = j + 'Butia'
                if blockstyle == 'basic-style-1arg':
                    palette.add_block(block_name,  # the name of your block
                    style=blockstyle,  # the block style
                    label=(label_name_from_device_id[j] + ' ' + _('Butia')),  # the label for the block
                    prim_name= block_name,  # code reference (see below)
                    default=[255],
                    help_string=_(modules_help[j])),
                    self.tw.lc.def_prim(block_name, 1, lambda self, x,y=j: primitive_dictionary[y + 'Butia'](x))
                else:
                    palette.add_block(block_name,  # the name of your block
                    style=blockstyle,  # the block style
                    label=(label_name_from_device_id[j] + ' ' + _('Butia')),  # the label for the block
                    prim_name= block_name,  # code reference (see below)
                    help_string=_(modules_help[j])),
                    self.tw.lc.def_prim(block_name, 0, lambda self, y=j: primitive_dictionary[y + 'Butia']())

                if (modules_name_from_device_id[j] in self.list_connected_device_module):
                    special_block_colors[block_name] = COLOR_PRESENT
                    BOX_COLORS[block_name] = COLOR_PRESENT
                else:
                    special_block_colors[block_name] = COLOR_NOTPRESENT
                    BOX_COLORS[block_name] = COLOR_NOTPRESENT
                    

                for k in range(1,MAX_SENSOR_PER_TYPE):
                    module = j + str(k)
                    block_name = module + 'Butia'
                    isHidden = True
                    if ((modules_name_from_device_id[j] + str(k)) in self.list_connected_device_module):
                        isHidden = False
                    if blockstyle == 'basic-style-1arg':
                        palette.add_block(block_name,  # the name of your block 
                                     style=blockstyle,  # the block style
                                     label=( label_name_from_device_id[j] + str(k) + ' ' +  _('Butia')),  # the label for the block
                                     prim_name= block_name,  # code reference (see below)
                                     help_string=_(modules_help[j]),
                                     default=[255],
                                     hidden=isHidden )
                        self.tw.lc.def_prim(block_name, 1, lambda self, x, y=k, z=j: primitive_dictionary[z + 'Butia'](x,y))
                    else:
                        palette.add_block(block_name,  # the name of your block   
                                     style=blockstyle,  # the block style
                                     label=(label_name_from_device_id[j] + str(k) + ' ' + _('Butia')),  # the label for the block
                                     prim_name= block_name,  # code reference (see below)
                                     help_string=_(modules_help[j]),
                                     hidden=isHidden )
                        self.tw.lc.def_prim(block_name, 0, lambda self, y=k , z=j: primitive_dictionary[z + 'Butia'](y))

                    if not(isHidden):
                        special_block_colors[block_name] = COLOR_PRESENT
                        BOX_COLORS[block_name] = COLOR_PRESENT
                    else:
                        special_block_colors[block_name] = COLOR_NOTPRESENT
                        BOX_COLORS[block_name] = COLOR_NOTPRESENT

        self.list_connected_device_module = []
        
        self.can_refresh = True

    def start(self):
        self.can_refresh = False

    #get the block name and returns the corresponding module name and its index
    #example: in: distance1Butia out: 1 , dist
    def block_2_index_and_name(self, block_name):
        """ Splits block_name in name and index, 
        returns a tuple (name,index)
        """
        result = self.regex.search(block_name)
        if result:
            return result.groups()
        else:
            return ('', 0)


    def refreshButia(self):
        if self.butia:
            self.butia.refresh()
            battery = self.butia.getBatteryCharge()
        else:
            battery = ERROR_SENSOR_READ
              
        COLOR_STATIC = self.staticBlocksColor(battery)
        COLOR_BATTERY = self.batteryColor(battery)

        #repaints program area blocks (proto) and palette blocks (block)
        for blk in self.tw.block_list.list:
            #NOTE: blocks types: proto, block, trash, deleted
            if blk.type in ['proto', 'block']:
                if (blk.name in static_block_list):
                    if (blk.name == 'batterychargeButia'):
                        BOX_COLORS[blk.name] = COLOR_BATTERY[:]
                    else:
                        BOX_COLORS[blk.name] = COLOR_STATIC[:]
                    blk.refresh()
                else:
                    blk_name, blk_index = self.block_2_index_and_name(blk.name)
                    if (blk_name in refreshable_block_list):
                        if blk_name in modules_name_from_device_id:
                            module_name = modules_name_from_device_id[blk_name] + blk_index
                        else:
                            module_name = ''
                        if module_name not in self.list_connected_device_module:
                            if blk_index !='' :
                                if blk.type == 'proto': # only make invisible the block in the palette not in the program area
                                    blk.set_visibility(False)
                            BOX_COLORS[blk.name] = COLOR_NOTPRESENT[:]
                        else:
                            if blk.type == 'proto': # don't has sense to change the visibility of a block in the program area
                                blk.set_visibility(True)
                            BOX_COLORS[blk.name] = COLOR_PRESENT[:]
                        blk.refresh()


        #impact changes in turtle blocks palette
        self.tw.show_toolbar_palette(palette_name_to_index('butia'), regenerate=True, show=True)	
  
    def change_butia_palette_colors(self):

        battery = self.butia.getBatteryCharge()
        if (battery == self.old_battery_value):
            change_statics_blocks = False
        else:
            change_statics_blocks = True
            self.old_battery_value = battery
            COLOR_STATIC = self.staticBlocksColor(battery)
            COLOR_BATTERY = self.batteryColor(battery)

        #repaints program area blocks (proto) and palette blocks (block)
        for blk in self.tw.block_list.list:
            #NOTE: blocks types: proto, block, trash, deleted
            if blk.type in ['proto', 'block']:
                if (blk.name in static_block_list):
                    if (change_statics_blocks):
                        if (blk.name == 'batterychargeButia'):
                            BOX_COLORS[blk.name] = COLOR_BATTERY[:]
                        else:
                            BOX_COLORS[blk.name] = COLOR_STATIC[:]
                        blk.refresh()
                else:
                    blk_name, blk_index = self.block_2_index_and_name(blk.name)
                    if (blk_name in refreshable_block_list):
                        if blk_name in modules_name_from_device_id:
                            module_name = modules_name_from_device_id[blk_name] + blk_index
                        else:
                            module_name = ''
                        if module_name in self.set_changed_device_module:
                            if module_name not in self.list_connected_device_module:
                                if blk_index !='' :
                                    if blk.type == 'proto': # only make invisible the block in the palette not in the program area
                                        blk.set_visibility(False)
                                BOX_COLORS[blk.name] = COLOR_NOTPRESENT[:]
                            else:
                                if blk.type == 'proto': # don't has sense to change the visibility of a block in the program area
                                    blk.set_visibility(True)
                                BOX_COLORS[blk.name] = COLOR_PRESENT[:]
                        blk.refresh()


        #impact changes in turtle blocks palette
        self.tw.show_toolbar_palette(palette_name_to_index('butia'), regenerate=True, show=False)	

    #if there exists new devices connected or disconections to the butia IO board, then it change the color of the blocks corresponding to the device 
    def check_for_device_change(self):
        
        old_list_connected_device_module =  self.list_connected_device_module
        self.list_connected_device_module = self.butia.get_modules_list()
        set_old_connected_device_module = set(old_list_connected_device_module)
        set_connected_device_module = set(self.list_connected_device_module)
        set_new_device_module = set_connected_device_module.difference(set_old_connected_device_module)
        set_old_device_module = set_old_connected_device_module.difference(set_connected_device_module)
        self.set_changed_device_module = set_new_device_module.union(set_old_device_module) # maybe exists one set operation for this

        if not(self.set_changed_device_module == set([])):
            self.change_butia_palette_colors()

    def stop(self):
        """ stop is called when stop button is pressed. """
        self.can_refresh = True
        if self.butia:
            self.butia.set2MotorSpeed('0', '0', '0', '0')

    def goto_background(self):
        """ goto_background is called when the activity is sent to the
        background. """
        pass

    def return_to_foreground(self):
        """ return_to_foreground is called when the activity returns to
        the foreground. """
        pass

    def quit(self):
        """ cleanup is called when the activity is exiting. """
        self.pollrun = False
        self.pollthread.cancel()
        if self.butia:
            self.butia.close()
            self.butia.closeService()
        if self.bobot:
            self.bobot.kill()

    def set_vels(self, left, right):
        if left > 0:
            sentLeft = "0"
        else:
            sentLeft = "1"
        if right > 0:
            sentRight = "0"
        else:
            sentRight = "1"
        if self.butia:
            self.butia.set2MotorSpeed(sentLeft, str(abs(left)), sentRight, str(abs(right)))

    def forwardButia(self):
        self.set_vels(self.actualSpeed, self.actualSpeed)
        #self.tw.canvas.setpen(True)
        #self.tw.canvas.forward(100)

    def forwardDistance(self, dist):
        #FIXME 8.29 para que velocidad? Vel = Dist / Tiempo => Tiempo = Dist / Vel
        tiempo = dist / 8.29
        self.set_vels(self.actualSpeed, self.actualSpeed)
        time.sleep(tiempo)
        self.set_vels(0, 0)
        #FIXME ir avanzando de a poquito en la espera de tiempo y no todo de golpe al final
        self.tw.canvas.setpen(True)
        self.tw.canvas.forward(dist)

    def backwardButia(self):
        self.set_vels(-self.actualSpeed, -self.actualSpeed)

    def backwardDistance(self, dist):
        #FIXME cambiar el 8.29 por valor que dependa de velocidad
        tiempo = dist / 8.29
        self.set_vels(-self.actualSpeed, -self.actualSpeed)
        time.sleep(tiempo)
        self.tw.canvas.setpen(True)
        self.tw.canvas.forward(-dist)
        self.set_vels(0, 0)

    def leftButia(self):
        self.set_vels(self.actualSpeed, -self.actualSpeed)

    def rightButia(self):
        self.set_vels(-self.actualSpeed, self.actualSpeed)

    def turnXdegree(self, degrees):
        #FIXME cambiar el 8.29 por valor que dependa de velocidad
        tiempo = (degrees * WHEELBASE * 3.14) / (360 * 8.29)
        if degrees > 0:
            self.set_vels(-self.actualSpeed, self.actualSpeed)
        else:
            self.set_vels(self.actualSpeed, -self.actualSpeed)
        time.sleep(abs(tiempo))
        self.tw.canvas.setpen(True)
        self.tw.canvas.arc(degrees, 0)
        self.set_vels(0, 0)

    def stopButia(self):
        self.set_vels(0, 0)

    def buttonButia(self, sensorid=''):
        if self.butia:
            return self.butia.getButton(sensorid)
        else:
            return ERROR_SENSOR_READ

    def batterychargeButia(self):
        if self.butia:
            return self.butia.getBatteryCharge()
        else:
            return ERROR_SENSOR_READ

    def batteryColor(self, battery):
        if (battery == -1): # or (battery == 255):
            return COLOR_NOTPRESENT
        elif ((battery < 254) and (battery >= 195)):
            return COLOR_PRESENT
        elif ((battery < 194) and (battery >= 134)):
            return ["#FFFF00","#808080"]
        elif ((battery < 134) and (battery >= 74)):
            return ["#FFA500","#808080"]
        else:
            return ["#FF0000","#808080"]

    def staticBlocksColor(self, battery):
        if (battery == -1) or (battery == 255) or (battery < 74):
            return COLOR_NOTPRESENT
        else:
            return COLOR_PRESENT

    def ambientlightButia(self, sensorid=''):
        if self.butia:
            return self.butia.getAmbientLight(sensorid)
        else:
            return ERROR_SENSOR_READ

    def distanceButia(self, sensorid=''):
        if self.butia:
            return self.butia.getDistance(sensorid)
        else:
            return ERROR_SENSOR_READ

    def grayscaleButia(self, sensorid=''):
        if self.butia:
            return self.butia.getGrayScale(sensorid)
        else:
            return ERROR_SENSOR_READ
        
    def temperatureButia(self, sensorid=''):
        if self.butia:
            return self.butia.getTemperature(sensorid)
        else:
            return ERROR_SENSOR_READ

    def vibrationButia(self, sensorid=''):
        if self.butia:
            return self.butia.getVibration(sensorid)
        else:
            return ERROR_SENSOR_READ

    def tiltButia(self, sensorid=''):
        if self.butia:
            return self.butia.getTilt(sensorid)
        else:
            return ERROR_SENSOR_READ

    def capacitivetouchButia(self, sensorid=''):
        if self.butia:
            return self.butia.getCapacitive(sensorid)
        else:
            return ERROR_SENSOR_READ

    def magneticinductionButia(self, sensorid=''):
        if self.butia:
            return self.butia.getMagneticInduction(sensorid)
        else:
            return ERROR_SENSOR_READ

    def LCDdisplayButia(self, text='________________________________'):
        if self.butia:
            self.butia.writeLCD(text)
        else:
            return ERROR_SENSOR_READ

    def ledButia(self, level, sensorid=''):
        if self.butia:
            self.butia.setLed(level)
        else:
            return ERROR_SENSOR_READ
    
    def speedButia(self, speed):
        if speed < 0:
            speed = -speed
        if speed > MAX_SPEED:
            speed = MAX_SPEED
        self.actualSpeed = speed

    def bobot_launch(self):
        """
        launch bobot-server.lua with a lua virtual machine modified to locally
        resolve library dependences located in the bin directory of tortugarte.
        And without libreadline and libhistory dependency
        """
        debug_output('initialising butia...')
        output = commands.getoutput('ps -ax | grep lua')
        if 'bobot-server' in output:
            debug_output('bobot is alive!')
        else:
            try:
                debug_output('creating bobot')
                self.bobot = subprocess.Popen(['./lua', 'bobot-server.lua'], cwd='./plugins/butia/butia_support')
            except:
                debug_output('ERROR creating bobot')

        self.butia = butiaAPI.robot()

        self.pollthread=threading.Timer(3,self.bobot_poll)
        self.pollthread.start()

    def bobot_poll(self):
        if self.pollrun:
            if self.can_refresh:
                self.butia.refresh()
                self.check_for_device_change()
            self.pollthread=threading.Timer(3,self.bobot_poll)
            self.pollthread.start()
        else:
            debug_output("Ending butia poll")

