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

from pybot import usb4butia
import time
import threading
import re
import subprocess
import commands

from TurtleArt.tapalette import special_block_colors
from TurtleArt.tapalette import palette_name_to_index
from TurtleArt.tapalette import make_palette
from TurtleArt.talogo import primitive_dictionary, logoerror
from TurtleArt.tautils import debug_output
from TurtleArt.tawindow import block_names

from plugins.plugin import Plugin

from gettext import gettext as _

#constants definitions
ERROR_SENSOR_READ = -1   # default return value in case of error when reading a sensor
MAX_SPEED = 1023   # max velocity for AX-12 - 10 bits -
MAX_SENSOR_PER_TYPE = 4
COLOR_NOTPRESENT = ["#A0A0A0","#808080"] 
COLOR_PRESENT = ["#00FF00","#008000"] #FIXME change for another tone of gray to avoid confusion with some similar blocks or the turtle
WHEELBASE = 28.00

ERROR_SPEED = _('the speed must be a value between 0 and 1023')
ERROR_PIN_NUMBER = _('the pin must be 1, 2, 3 or 4')
ERROR_PIN_VALUE = _('the value must be 0 or 1')

#Dictionary for help string asociated to modules used for automatic generation of block instances
modules_help = {} 
modules_help['led'] = _("adjust LED intensity between 0 and 255")
modules_help['grayscale'] = _("returns the gray level")
modules_help['button'] = _("returns 1 when the button is press and 0 otherwise")
modules_help['ambientlight'] = _("returns the ambient light level")
modules_help['temperature'] = _("returns the ambient temperature")
modules_help['distance'] = _("returns the distance from the object in front of the sensor")
modules_help['tilt'] = _("returns 0 or 1 depending on the sensor inclination")
modules_help['magneticinduction'] = _("returns 1 when the sensors detects a magnetic field, 0 otherwise")
modules_help['vibration'] = _("switches from 0 to 1, the frequency depends on the vibration")
modules_help['resistanceB'] = _("returns the value of the resistance")
modules_help['voltajeB'] = _("returns the value of the voltaje")


#Dictionary for translating block name to module name used for automatic generation of block instances
modules_name_from_device_id = {} 
modules_name_from_device_id['led'] = 'led'
modules_name_from_device_id['button'] = 'button'
modules_name_from_device_id['grayscale'] = 'grey'
modules_name_from_device_id['ambientlight'] = 'light'
modules_name_from_device_id['temperature'] = 'temp'
modules_name_from_device_id['distance'] = 'distanc'
modules_name_from_device_id['resistanceB'] = 'res'
modules_name_from_device_id['voltajeB'] = 'volt'

device_id_from_module_name = {} 
device_id_from_module_name['led'] = 'led'
device_id_from_module_name['button'] = 'button'
device_id_from_module_name['grey'] = 'grayscale'
device_id_from_module_name['light'] = 'ambientlight'
device_id_from_module_name['temp'] = 'temperature'
device_id_from_module_name['distanc'] = 'distance'
device_id_from_module_name['res'] = 'resistance'
device_id_from_module_name['volt'] = 'voltaje'

label_name_from_device_id= {} 
label_name_from_device_id['led'] = _('LED')
label_name_from_device_id['button'] = _('button')
label_name_from_device_id['grayscale'] = _('grayscale')
label_name_from_device_id['ambientlight'] = _('ambient light')
label_name_from_device_id['temperature'] = _('temperature')
label_name_from_device_id['distance'] = _('distance')
label_name_from_device_id['resistanceB'] = _('resistance')
label_name_from_device_id['voltajeB'] = _('voltaje')

refreshable_block_list = ['ambientlight', 'grayscale', 'temperature', 'distance', 'button', 'led', 'resistanceB', 'voltajeB']

static_block_list = ['forwardButia', 'backwardButia', 'leftButia', 'rightButia', 'stopButia', 'speedButia', 'batterychargeButia', 'moveButia']

class Butia(Plugin):
    
    def __init__(self, parent):
        self.tw = parent
        # Enable extra palette
        self.extra_palette = True
        self.actualSpeed = [600, 600]
        self.butia = None
        self.pollthread = None
        self.pollrun = True
        self.battery_value = ERROR_SENSOR_READ
        self.old_battery_value = ERROR_SENSOR_READ
        self.hack_pins = ['0', '0', '0', '0']
        self.bobot = None
        self.butia = None
        self.match_list = []
        self.list_connected_device_module = []
        self.pollthread = threading.Timer(0, self.pybot_launch)
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

        palette = make_palette('butia', colors=COLOR_NOTPRESENT, help_string=_('Butia Robot'))
        if self.extra_palette:
            palette2 = make_palette('butia-extra', colors=COLOR_NOTPRESENT, help_string=_('Butia Robot extra blocks'))

        if self.butia:
            self.battery_value = self.butia.getBatteryCharge()
        else:
            self.battery_value = ERROR_SENSOR_READ

        COLOR_STATIC = self.staticBlocksColor(self.battery_value)
        COLOR_BATTERY = self.batteryColor(self.battery_value)

        #add block about movement of butia, this blocks don't allow multiple instances

        primitive_dictionary['refreshButia'] = self.refreshButia
        palette.add_block('refreshButia',
                     style='basic-style',
                     label=_('refresh Butia'),
                     prim_name='refreshButia',
                     help_string=_('refresh the state of the Butia palette and blocks'))
        self.tw.lc.def_prim('refreshButia', 0, lambda self: primitive_dictionary['refreshButia']())
        special_block_colors['refreshButia'] = COLOR_PRESENT[:]

        primitive_dictionary['batterychargeButia'] = self.batterychargeButia
        palette.add_block('batterychargeButia',
                     style='box-style',
                     label=_('battery charge Butia'),
                     prim_name='batterychargeButia',
                     help_string=_('returns the battery charge as a number between 0 and 255'))
        self.tw.lc.def_prim('batterychargeButia', 0, lambda self: primitive_dictionary['batterychargeButia']())
        special_block_colors['batterychargeButia'] = COLOR_BATTERY[:]

        primitive_dictionary['speedButia'] = self.speedButia
        palette.add_block('speedButia',
                     style='basic-style-1arg',
                     label=[_('speed Butia')],
                     prim_name='speedButia',
                     default=[600],
                     help_string=_('set the speed of the Butia motors'))
        self.tw.lc.def_prim('speedButia', 1, lambda self, x: primitive_dictionary['speedButia'](x))
        special_block_colors['speedButia'] = COLOR_STATIC[:]
        
        primitive_dictionary['moveButia'] = self.moveButia
        palette.add_block('moveButia',
                     style='basic-style-2arg',
                     label=[_('move Butia'), _('left'), _('right')],
                     prim_name='moveButia',
                     default=[600, 600],
                     help_string=_('moves the Butia motors at the specified speed'))
        self.tw.lc.def_prim('moveButia', 2, lambda self, x, y: primitive_dictionary['moveButia'](x, y))
        special_block_colors['moveButia'] = COLOR_STATIC[:]

        primitive_dictionary['stopButia'] = self.stopButia
        palette.add_block('stopButia',
                     style='basic-style',
                     label=_('stop Butia'),
                     prim_name='stopButia',
                     help_string=_('stop the Butia robot'))
        self.tw.lc.def_prim('stopButia', 0, lambda self: primitive_dictionary['stopButia']())
        special_block_colors['stopButia'] = COLOR_STATIC[:]

        primitive_dictionary['forwardButia'] = self.forwardButia
        palette.add_block('forwardButia',
                     style='basic-style',
                     label=_('forward Butia'),
                     prim_name='forwardButia',
                     help_string=_('move the Butia robot forward'))
        self.tw.lc.def_prim('forwardButia', 0, lambda self: primitive_dictionary['forwardButia']())
        special_block_colors['forwardButia'] = COLOR_STATIC[:]

        primitive_dictionary['leftButia'] = self.leftButia
        palette.add_block('leftButia',
                     style='basic-style',
                     label=_('left Butia'),
                     prim_name='leftButia',
                     help_string=_('turn the Butia robot at left'))
        self.tw.lc.def_prim('leftButia', 0, lambda self: primitive_dictionary['leftButia']())
        special_block_colors['leftButia'] = COLOR_STATIC[:]
        
        primitive_dictionary['rightButia'] = self.rightButia
        palette.add_block('rightButia',
                     style='basic-style',
                     label=_('right Butia'),
                     prim_name='rightButia',
                     help_string=_('turn the Butia robot at right'))
        self.tw.lc.def_prim('rightButia', 0, lambda self: primitive_dictionary['rightButia']())
        special_block_colors['rightButia'] = COLOR_STATIC[:]

        primitive_dictionary['backwardButia'] = self.backwardButia
        palette.add_block('backwardButia',
                     style='basic-style',
                     label=_('backward Butia'),
                     prim_name='backwardButia',
                     help_string=_('move the Butia robot backward'))
        self.tw.lc.def_prim('backwardButia', 0, lambda self: primitive_dictionary['backwardButia']())
        special_block_colors['backwardButia'] = COLOR_STATIC[:]

        if self.extra_palette:
            primitive_dictionary['setpinButia'] = self.setpinButia
            palette2.add_block('setpinButia',
                         style='basic-style-2arg',
                         label=[_('set hack pin Butia'), _('pin'), _('value')],
                         prim_name='setpinButia',
                         #default=[None, None],
                         help_string=_('set a hack pin to 0 or 1'))
            self.tw.lc.def_prim('setpinButia', 2, lambda self, x, y: primitive_dictionary['setpinButia'](x, y))
            special_block_colors['setpinButia'] = COLOR_STATIC[:]


        #add every function in the code 
        primitive_dictionary['ledButia'] = self.ledButia
        primitive_dictionary['ambientlightButia'] = self.ambientlightButia
        primitive_dictionary['grayscaleButia'] = self.grayscaleButia
        primitive_dictionary['buttonButia'] = self.buttonButia
        primitive_dictionary['temperatureButia'] = self.temperatureButia
        primitive_dictionary['distanceButia'] = self.distanceButia
        primitive_dictionary['resistanceBButia'] = self.resistanceB
        primitive_dictionary['voltajeBButia'] = self.voltajeB

        #generic mecanism to add sensors that allows multiple instances, depending on the number of instances connected to the 
        #physical robot the corresponding block appears in the pallete

        for i in [   ['basic-style-1arg', ['led']],
                     ['box-style', ['button', 'grayscale', 'ambientlight', 'temperature', 'distance', 'resistanceB', 'voltajeB']]
                 ]:

            (blockstyle , listofmodules) = i
            for j in listofmodules:
                for m in range(0, MAX_SENSOR_PER_TYPE):
                    isHidden = True
                    k = m
                    if (m == 0):
                        isHidden = False
                        k = ''

                    module = j + str(k)
                    block_name = module + 'Butia'
                    
                    if (j == 'resistanceB') or (j == 'voltajeB'):
                        if self.extra_palette:
                            palette2.add_block(block_name, 
                                     style=blockstyle,
                                     label=(label_name_from_device_id[j] + str(k) + ' ' +  _('Butia')),
                                     prim_name= block_name,
                                     help_string=_(modules_help[j]),
                                     hidden=isHidden)
                    else:
                        palette.add_block(block_name, 
                                 style=blockstyle,
                                 label=(label_name_from_device_id[j] + str(k) + ' ' +  _('Butia')),
                                 prim_name= block_name,
                                 help_string=_(modules_help[j]),
                                 hidden=isHidden)

                    if blockstyle == 'basic-style-1arg':
                        self.tw.lc.def_prim(block_name, 1, lambda self, x, y=k, z=j: primitive_dictionary[z + 'Butia'](x,y))
                    else:
                        self.tw.lc.def_prim(block_name, 0, lambda self, y=k , z=j: primitive_dictionary[z + 'Butia'](y))

                    special_block_colors[block_name] = COLOR_NOTPRESENT[:]


    def start(self):
        self.can_refresh = False

    def block_2_index_and_name(self, block_name):
        """ Splits block_name in name and index, 
        returns a tuple (name,index)
        """
        result = self.regex.search(block_name)
        if result:
            return result.groups()
        else:
            return ('', 0)

    def list_2_module_and_port(self, l):
        r = []
        for e in l:
            try:
                module, port = e.split(':')
                if module in device_id_from_module_name:
                    r.append((port, module))
            except:
                pass
        return r

    def make_match_dict(self, l):
        match_list = []
        for t in l:
            i = 0
            for index in range(0, int(t[0])):
                x = (str(index), t[1])
                if x in l:
                    i = i + 1
            if i == 0:
                match_list.append((t[1], t[0]))
            else:
                match_list.append((t[1] + str(i), t[0]))
        return dict(match_list)

    def refreshButia(self):
        if self.butia:
            self.butia.refresh()
        self.check_for_device_change(True)
  
    def change_butia_palette_colors(self, change_statics_blocks):

        COLOR_STATIC = self.staticBlocksColor(self.battery_value)
        COLOR_BATTERY = self.batteryColor(self.battery_value)

        self.refresh_palette_2(COLOR_STATIC, COLOR_BATTERY, change_statics_blocks)

        try:
            index = palette_name_to_index('butia')
            self.tw.regenerate_palette(index)
            if self.extra_palette:
                index = palette_name_to_index('butia-extra')
                self.tw.regenerate_palette(index)
        except:
            pass


    def refresh_palette_2(self, COLOR_STATIC, COLOR_BATTERY, change_statics_blocks):

        l = self.list_2_module_and_port(self.list_connected_device_module)
        self.match_dict = self.make_match_dict(l)

        #repaints program area blocks (proto) and palette blocks (block)
        for blk in self.tw.block_list.list:
            #NOTE: blocks types: proto, block, trash, deleted
            if blk.type in ['proto', 'block']:
                if (blk.name in static_block_list):
                    if (change_statics_blocks):
                        if (blk.name == 'batterychargeButia'):
                            special_block_colors[blk.name] = COLOR_BATTERY[:]
                        else:
                            special_block_colors[blk.name] = COLOR_STATIC[:]
                        blk.refresh()
                else:
                    blk_name, blk_index = self.block_2_index_and_name(blk.name)
                    if (blk_name in refreshable_block_list):
                        module = modules_name_from_device_id[blk_name]
                        s = module + blk_index
                        if not(s in self.match_dict):
                            if blk_index !='' :
                                if blk.type == 'proto': # only make invisible the block in the palette not in the program area
                                    blk.set_visibility(False)

                            label = label_name_from_device_id[blk_name] + ' ' + _('Butia')
                            value = blk_index
                            special_block_colors[blk.name] = COLOR_NOTPRESENT[:]
                        else:
                            val = self.match_dict[s]
                            value = int(val)
                            label = label_name_from_device_id[blk_name] + ':' + val + ' ' + _('Butia')
                            if blk.type == 'proto': # don't has sense to change the visibility of a block in the program area
                                blk.set_visibility(True)
                            special_block_colors[blk.name] = COLOR_PRESENT[:]

                        if module == 'led':
                            self.tw.lc.def_prim(blk.name, 1, lambda self, x, y=value, z=blk_name: primitive_dictionary[z+ 'Butia'](x,y))
                        else:
                            self.tw.lc.def_prim(blk.name, 0, lambda self, y=value, z=blk_name: primitive_dictionary[z+ 'Butia'](y))

                        blk.spr.set_label(label)
                        block_names[blk.name][0] = label
                        blk.refresh()


    def check_for_device_change(self, force_refresh):
        """ if there exists new devices connected or disconections to the butia IO board, 
         then it change the color of the blocks corresponding to the device """
        
        old_list_connected_device_module =  self.list_connected_device_module

        if self.butia:
            self.list_connected_device_module = self.butia.get_modules_list()
            self.battery_value = self.butia.getBatteryCharge()
        else:
            self.list_connected_device_module = []
            self.battery_value = ERROR_SENSOR_READ

        set_old_connected_device_module = set(old_list_connected_device_module)
        set_connected_device_module = set(self.list_connected_device_module)
        set_new_device_module = set_connected_device_module.difference(set_old_connected_device_module)
        set_old_device_module = set_old_connected_device_module.difference(set_connected_device_module)
        self.set_changed_device_module = set_new_device_module.union(set_old_device_module) # maybe exists one set operation for this

        if force_refresh:
            self.change_butia_palette_colors(True)
        else:
            change_statics_blocks = False
            if not(self.battery_value == self.old_battery_value):
                change_statics_blocks = True
                self.old_battery_value = self.battery_value

            if not(self.set_changed_device_module == set([])) or change_statics_blocks:
                self.change_butia_palette_colors(change_statics_blocks)

    def stop(self):
        """ stop is called when stop button is pressed. """
        self.can_refresh = True
        if self.butia:
            self.butia.set2MotorSpeed(0, 0, 0, 0)

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
        left = int(left)
        right = int(right)
        if left > 0:
            sentLeft = 0
        else:
            sentLeft = 1
        if right > 0:
            sentRight = 0
        else:
            sentRight = 1
        if self.butia:
            self.butia.set2MotorSpeed(sentLeft, abs(left), sentRight, abs(right))

    def moveButia(self, left, right):
        self.set_vels(left, right)

    def forwardButia(self):
        self.set_vels(self.actualSpeed[0], self.actualSpeed[1])
        #self.tw.canvas.setpen(True)
        #self.tw.canvas.forward(100)

    def backwardButia(self):
        self.set_vels(-self.actualSpeed[0], -self.actualSpeed[1])

    def leftButia(self):
        self.set_vels(self.actualSpeed[0], -self.actualSpeed[1])

    def rightButia(self):
        self.set_vels(-self.actualSpeed[0], self.actualSpeed[1])

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
        if (battery == -1):
            return COLOR_NOTPRESENT[:]
        elif ((battery < 254) and (battery >= 74)):
            return ["#FFA500","#808080"]
        else:
            return ["#FF0000","#808080"]

    def staticBlocksColor(self, battery):
        if (battery == -1) or (battery == 255) or (battery < 74):
            return COLOR_NOTPRESENT[:]
        else:
            return COLOR_PRESENT[:]

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

    def resistanceB(self, sensorid=''):
        if self.butia:
            return self.butia.getResistance(sensorid)
        else:
            return ERROR_SENSOR_READ

    def voltajeB(self, sensorid=''):
        if self.butia:
            return self.butia.getVoltaje(sensorid)
        else:
            return ERROR_SENSOR_READ

    def capacitivetouchButia(self, sensorid=''):
        if self.butia:
            return self.butia.getCapacitive(sensorid)
        else:
            return ERROR_SENSOR_READ


    def ledButia(self, level, sensorid=''):
        if self.butia:
            self.butia.setLed(level, sensorid)
        else:
            return ERROR_SENSOR_READ
    
    def speedButia(self, speed):
        if (speed < 0) or (speed > MAX_SPEED):
            raise logoerror(ERROR_SPEED)
        self.actualSpeed = [speed, speed]

    def setpinButia(self, pin, value):
        if self.butia:
            pin = int(pin - 1)
            if (pin < 0) or (pin > 3):
                raise logoerror(ERROR_PIN_NUMBER)
            else:
                if (value < 0) or (value > 1):
                    raise logoerror(ERROR_PIN_VALUE)
                else:
                    self.hack_pins[pin] = str(value)
                    self.butia.setHacks(self.hack_pins[0], self.hack_pins[1], self.hack_pins[2], self.hack_pins[3])
        else:
            return ERROR_SENSOR_READ

    def pybot_launch(self):

        self.butia = usb4butia.USB4Butia()

        self.pollthread=threading.Timer(3, self.bobot_poll)
        self.pollthread.start()

    def bobot_poll(self):
        if self.pollrun:
            if (self.tw.activity.init_complete and self.can_refresh):
                self.butia.refresh()
                self.check_for_device_change(False)
            self.pollthread=threading.Timer(3, self.bobot_poll)
            self.pollthread.start()
        else:
            debug_output("Ending butia poll")

