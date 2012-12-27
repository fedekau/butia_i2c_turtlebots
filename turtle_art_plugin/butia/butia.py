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
ERROR = -1   # default return value in case of error
MAX_SPEED = 1023   # max velocity for AX-12 - 10 bits -
MAX_SENSOR_PER_TYPE = 5
COLOR_NOTPRESENT = ["#A0A0A0","#808080"] 
COLOR_PRESENT = ["#00FF00","#008000"] #FIXME change for another tone of gray to avoid confusion with some similar blocks or the turtle

ERROR_SPEED = _('ERROR: The speed must be a value between 0 and 1023')
ERROR_PIN_NUMBER = _('ERROR: The pin must be between 1 and 8')
ERROR_PIN_VALUE = _('ERROR: The value must be 0 or 1, LOW or HIGH')
ERROR_PIN_MODE = _('ERROR: The mode must be INPUT or OUTPUT.')

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
modules_help['voltageB'] = _("returns the value of the voltage")
modules_help['gpio'] = _("gpio")

#Dictionary for translating block name to module name used for automatic generation of block instances
modules_name_from_device_id = {} 
modules_name_from_device_id['led'] = 'led'
modules_name_from_device_id['button'] = 'button'
modules_name_from_device_id['grayscale'] = 'grey'
modules_name_from_device_id['ambientlight'] = 'light'
modules_name_from_device_id['temperature'] = 'temp'
modules_name_from_device_id['distance'] = 'distanc'
modules_name_from_device_id['resistanceB'] = 'res'
modules_name_from_device_id['voltageB'] = 'volt'
modules_name_from_device_id['gpio'] = 'gpio'

device_id_from_module_name = {} 
device_id_from_module_name['led'] = 'led'
device_id_from_module_name['button'] = 'button'
device_id_from_module_name['grey'] = 'grayscale'
device_id_from_module_name['light'] = 'ambientlight'
device_id_from_module_name['temp'] = 'temperature'
device_id_from_module_name['distanc'] = 'distance'
device_id_from_module_name['res'] = 'resistance'
device_id_from_module_name['volt'] = 'voltage'
device_id_from_module_name['gpio'] = 'gpio'

label_name_from_device_id= {} 
label_name_from_device_id['led'] = _('LED')
label_name_from_device_id['button'] = _('button')
label_name_from_device_id['grayscale'] = _('grayscale')
label_name_from_device_id['ambientlight'] = _('ambient light')
label_name_from_device_id['temperature'] = _('temperature')
label_name_from_device_id['distance'] = _('distance')
label_name_from_device_id['resistanceB'] = _('resistance')
label_name_from_device_id['voltageB'] = _('voltage')
label_name_from_device_id['gpio'] = _('gpio')

refreshable_block_list = ['ambientlight', 'grayscale', 'temperature', 'distance', 'button', 'led', 'resistanceB', 'voltageB', 'gpio']
static_block_list = ['forwardButia', 'backwardButia', 'leftButia', 'rightButia', 'stopButia', 'speedButia', 'batterychargeButia', 'moveButia']
extras_block_list = ['setpinButia', 'getpinButia', 'pinmodeButia', 'highButia', 'lowButia', 'inputButia', 'outputButia']

class Butia(Plugin):
    
    def __init__(self, parent):
        self.tw = parent
        self.actualSpeed = [600, 600]
        self.hack_states = [1, 1, 1, 1, 1, 1, 1, 1]
        self.butia = None
        self.pollthread = None
        self.pollrun = True
        self.battery_value = ERROR
        self.old_battery_value = ERROR
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

        palette = make_palette('butia', colors=COLOR_NOTPRESENT, help_string=_('Butia Robot'), init_on_start=True)

        self.battery_value = self.batterychargeButia()
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

        # Extra palette
        palette2 = make_palette('butia-extra', colors=COLOR_NOTPRESENT, help_string=_('Butia Robot extra blocks'), init_on_start=True)

        primitive_dictionary['pinmodeButia'] = self.pinmodeButia
        palette2.add_block('pinmodeButia',
                  style='basic-style-2arg',
                  label=[_('hack pin mode'),_('pin'),_('mode')],
                  help_string=_('Select the pin function (INPUT, OUTPUT).'),
                  default=[1],
                  prim_name='pinmodeButia')
        self.tw.lc.def_prim('pinmodeButia', 2, lambda self, x, y: primitive_dictionary['pinmodeButia'](x, y))
        special_block_colors['pinmodeButia'] = COLOR_STATIC[:]

        primitive_dictionary['setpinButia'] = self.setpinButia
        palette2.add_block('setpinButia',
                     style='basic-style-2arg',
                     label=[_('write hack pin Butia'), _('pin'), _('value')],
                     prim_name='setpinButia',
                     default=[1, 0],
                     help_string=_('set a hack pin to 0 or 1'))
        self.tw.lc.def_prim('setpinButia', 2, lambda self, x, y: primitive_dictionary['setpinButia'](x, y))
        special_block_colors['setpinButia'] = COLOR_STATIC[:]

        primitive_dictionary['getpinButia'] = self.getpinButia
        palette2.add_block('getpinButia',
                     style='number-style-1arg',
                     label=[_('read hack pin Butia')],
                     prim_name='getpinButia',
                     default=1,
                     help_string=_('read the value of a hack pin'))
        self.tw.lc.def_prim('getpinButia', 1, lambda self, x: primitive_dictionary['getpinButia'](x))
        special_block_colors['getpinButia'] = COLOR_STATIC[:]

        primitive_dictionary['highButia'] = self.highButia
        palette2.add_block('highButia',
                  style='box-style',
                  label=_('HIGH'),
                  help_string=_('Set HIGH value for digital port.'),
                  prim_name='highButia')
        self.tw.lc.def_prim('highButia', 0, lambda self: primitive_dictionary['highButia']())
        special_block_colors['highButia'] = COLOR_STATIC[:]

        primitive_dictionary['inputButia'] = self.inputButia
        palette2.add_block('inputButia',
                  style='box-style',
                  label=_('INPUT'),
                  help_string=_('Configure hack port for digital input.'),
                  prim_name='inputButia')
        self.tw.lc.def_prim('inputButia', 0, lambda self: primitive_dictionary['inputButia']())
        special_block_colors['inputButia'] = COLOR_STATIC[:]

        primitive_dictionary['lowButia'] = self.lowButia
        palette2.add_block('lowButia',
                  style='box-style',
                  label=_('LOW'),
                  help_string=_('Set LOW value for digital port.'),
                  prim_name='lowButia')
        self.tw.lc.def_prim('lowButia', 0, lambda self: primitive_dictionary['lowButia']())
        special_block_colors['lowButia'] = COLOR_STATIC[:]

        primitive_dictionary['outputButia'] = self.outputButia
        palette2.add_block('outputButia',
                  style='box-style',
                  label=_('OUTPUT'),
                  help_string=_('Configure hack port for digital output.'),
                  prim_name='outputButia')
        self.tw.lc.def_prim('outputButia', 0, lambda self: primitive_dictionary['outputButia']())
        special_block_colors['outputButia'] = COLOR_STATIC[:]


        #add every function in the code 
        primitive_dictionary['ledButia'] = self.ledButia
        primitive_dictionary['ambientlightButia'] = self.ambientlightButia
        primitive_dictionary['grayscaleButia'] = self.grayscaleButia
        primitive_dictionary['buttonButia'] = self.buttonButia
        primitive_dictionary['temperatureButia'] = self.temperatureButia
        primitive_dictionary['distanceButia'] = self.distanceButia
        primitive_dictionary['resistanceBButia'] = self.resistanceButia
        primitive_dictionary['voltageBButia'] = self.voltageButia
        primitive_dictionary['gpioButia'] = self.gpioButia

        #generic mecanism to add sensors that allows multiple instances, depending on the number of instances connected to the 
        #physical robot the corresponding block appears in the pallete

        for i in [   ['basic-style-1arg', ['led']],
                     ['box-style', ['button', 'grayscale', 'ambientlight', 'temperature', 'distance', 'resistanceB', 'voltageB', 'gpio']]
                 ]:

            (blockstyle , listofmodules) = i
            for j in listofmodules:
                for m in range(MAX_SENSOR_PER_TYPE):
                    isHidden = True
                    k = m
                    if (m == 0):
                        isHidden = False
                        k = ''

                    module = j + str(k)
                    block_name = module + 'Butia'
                    
                    if (j == 'resistanceB') or (j == 'voltageB') or (j == 'gpio'):
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
                        self.tw.lc.def_prim(block_name, 1, lambda self, w, x=k, y=j, z=0: primitive_dictionary[y + 'Butia'](w, x, z))
                    else:
                        self.tw.lc.def_prim(block_name, 0, lambda self, x=k, y=j, z=0: primitive_dictionary[y + 'Butia'](x, z))

                    special_block_colors[block_name] = COLOR_NOTPRESENT[:]


    ################################ Turtle calls ################################

    def start(self):
        self.can_refresh = False

    def stop(self):
        self.set_vels(0, 0)
        self.can_refresh = True

    def goto_background(self):
        pass

    def return_to_foreground(self):
        pass

    def quit(self):
        self.pollrun = False
        self.pollthread.cancel()
        if self.butia:
            self.butia.close()
        if self.bobot:
            self.bobot.kill()

    ################################ Refresh process ################################

    def refreshButia(self):
        if self.butia:
            self.butia.refresh()
        self.check_for_device_change(True)

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

    def block_2_index_and_name(self, block_name):
        """ Splits block_name in name and index, 
        returns a tuple (name,index)
        """
        result = self.regex.search(block_name)
        if result:
            return result.groups()
        else:
            return ('', 0)

    def complete_dict(self):
        self.m_d = {}
        for d in device_id_from_module_name.keys():
            self.m_d[d] = 0

    def list_2_module_and_port(self, l):
        r = []
        for e in l:
            try:
                m_b, port = e.split(':')
                if m_b.count('@') == 0:
                    module = m_b
                    board = '0'
                else:
                    module, board = m_b.split('@')
                if module in device_id_from_module_name:
                    r.append((port, module, board))
            except:
                pass
        return r

    def make_match_dict(self, l):
        self.complete_dict()
        match_list = []
        for t in l:
            module = t[1]
            n = self.m_d[module]
            self.m_d[module] = self.m_d[module] + 1
            if n == 0:
                match_list.append((module, (t[0], t[2])))
            else:
                match_list.append((module + str(n), (t[0], t[2])))

        return dict(match_list)

    def change_butia_palette_colors(self, change_statics_blocks, board_present):

        COLOR_STATIC = self.staticBlocksColor(self.battery_value)
        COLOR_BATTERY = self.batteryColor(self.battery_value)
        if board_present:
            COLOR_EXTRAS = COLOR_PRESENT[:]
        else:
            COLOR_EXTRAS = COLOR_NOTPRESENT[:]

        self.refresh_palette_2(COLOR_STATIC, COLOR_BATTERY, COLOR_EXTRAS, change_statics_blocks)

        try:
            index = palette_name_to_index('butia')
            self.tw.regenerate_palette(index)
        except:
            pass

        try:
            index = palette_name_to_index('butia-extra')
            self.tw.regenerate_palette(index)
        except:
            pass

    def refresh_palette_2(self, COLOR_STATIC, COLOR_BATTERY, COLOR_EXTRAS, change_statics_blocks):

        l = self.list_2_module_and_port(self.list_connected_device_module)
        self.match_dict = self.make_match_dict(l)

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
                elif (blk.name in extras_block_list):
                    special_block_colors[blk.name] = COLOR_EXTRAS[:]
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
                            board = 0
                            special_block_colors[blk.name] = COLOR_NOTPRESENT[:]
                        else:
                            val = self.match_dict[s]
                            value = int(val[0])
                            board = int(val[1])
                            label = label_name_from_device_id[blk_name] + ':' + val[0] + ' ' + _('Butia')
                            if butias > 1:
                                label = label + ' ' + val[1]

                            if blk.type == 'proto': # don't has sense to change the visibility of a block in the program area
                                blk.set_visibility(True)
                            special_block_colors[blk.name] = COLOR_PRESENT[:]

                        if module == 'led':
                            self.tw.lc.def_prim(blk.name, 1, lambda self, w, x=value, y=blk_name, z=board: primitive_dictionary[y + 'Butia'](w,x, z))
                        else:
                            self.tw.lc.def_prim(blk.name, 0, lambda self, x=value, y=blk_name, z=board: primitive_dictionary[y+ 'Butia'](x, z))

                        blk.spr.set_label(label)
                        block_names[blk.name][0] = label
                        blk.refresh()

    def check_for_device_change(self, force_refresh):
        """ if there exists new devices connected or disconections to the butia IO board, 
         then it change the color of the blocks corresponding to the device """
        
        old_list_connected_device_module = self.list_connected_device_module[:]

        if self.butia:
            self.list_connected_device_module = self.butia.get_modules_list()
        else:
            self.list_connected_device_module = []

        self.battery_value = self.batterychargeButia()
        
        if not(self.list_connected_device_module == []):
            board_present = True
        else:
            board_present = False

        if force_refresh:
            self.change_butia_palette_colors(True, board_present)
        else:
            change_statics_blocks = False
            if not(self.battery_value == self.old_battery_value):
                change_statics_blocks = True
                self.old_battery_value = self.battery_value

            if not(old_list_connected_device_module == self.list_connected_device_module) or change_statics_blocks:
                self.change_butia_palette_colors(change_statics_blocks, board_present)

    ################################ Movement calls ################################

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

    def backwardButia(self):
        self.set_vels(-self.actualSpeed[0], -self.actualSpeed[1])

    def leftButia(self):
        self.set_vels(self.actualSpeed[0], -self.actualSpeed[1])

    def rightButia(self):
        self.set_vels(-self.actualSpeed[0], self.actualSpeed[1])

    def stopButia(self):
        self.set_vels(0, 0)

    def speedButia(self, speed):
        if (speed < 0) or (speed > MAX_SPEED):
            raise logoerror(ERROR_SPEED)
        self.actualSpeed = [speed, speed]

    ################################ Sensors calls ################################

    def batterychargeButia(self):
        if self.butia:
            return self.butia.getBatteryCharge()
        else:
            return ERROR

    def buttonButia(self, sensorid='', boardid=''):
        if self.butia:
            return self.butia.getButton(sensorid, boardid)
        else:
            return ERROR

    def ambientlightButia(self, sensorid='', boardid=''):
        if self.butia:
            return self.butia.getAmbientLight(sensorid, boardid)
        else:
            return ERROR

    def distanceButia(self, sensorid='', boardid=''):
        if self.butia:
            return self.butia.getDistance(sensorid, boardid)
        else:
            return ERROR

    def grayscaleButia(self, sensorid='', boardid=''):
        if self.butia:
            return self.butia.getGrayScale(sensorid, boardid)
        else:
            return ERROR
        
    def temperatureButia(self, sensorid='', boardid=''):
        if self.butia:
            return self.butia.getTemperature(sensorid, boardid)
        else:
            return ERROR

    def resistanceButia(self, sensorid='', boardid=''):
        if self.butia:
            return self.butia.getResistance(sensorid, boardid)
        else:
            return ERROR

    def voltageButia(self, sensorid='', boardid=''):
        if self.butia:
            return self.butia.getVoltage(sensorid, boardid)
        else:
            return ERROR

    def gpioButia(self, sensorid='', boardid=''):
        if self.butia:
            return self.butia.getGpio(sensorid, boardid)
        else:
            return ERROR

    def ledButia(self, on_off, sensorid='', boardid=''):
        if self.butia:
            self.butia.setLed(on_off, sensorid, boardid)
        else:
            return ERROR

    ################################ Extras ################################

    def pinmodeButia(self, pin, mode):
        if self.butia:
            pin = int(pin)
            pin = pin - 1
            if (pin < 0) or (pin > 7):
                raise logoerror(ERROR_PIN_NUMBER)
            else:
                if mode == _('INPUT'):
                    self.hack_states[pin] = 1
                    self.butia.modeHack(pin, 1)
                elif mode == _('OUTPUT'):
                    self.hack_states[pin] = 0
                    self.butia.modeHack(pin, 0)
                else:
                    raise logoerror(ERROR_PIN_MODE)
        else:
            return ERROR

    def highButia(self):
        return 1

    def lowButia(self):
        return 0

    def inputButia(self):
        return _('INPUT')

    def outputButia(self):
        return _('OUTPUT')

    def setpinButia(self, pin, value):
        if self.butia:
            pin = int(pin)
            pin = pin - 1
            if (pin < 0) or (pin > 7):
                raise logoerror(ERROR_PIN_NUMBER)
            else:
                if self.hack_states[pin] == 1:
                    raise logoerror(_('ERROR: The pin %s must be in OUTPUT mode.'))
                else:
                    if (value < 0) or (value > 1):
                        raise logoerror(ERROR_PIN_VALUE)
                    else:
                        self.butia.setHack(pin, value)
        else:
            return ERROR

    def getpinButia(self, pin):
        if self.butia:
            pin = int(pin)
            pin = pin - 1
            if (pin < 0) or (pin > 7):
                raise logoerror(ERROR_PIN_NUMBER)
            else:
                if self.hack_states[pin] == 0:
                    raise logoerror(_('ERROR: The pin %s must be in INPUT mode.'))
                else:
                    return self.butia.getHack(pin)
        else:
            return ERROR

    ################################ pybot and thread ################################

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

