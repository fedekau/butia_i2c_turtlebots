#! /usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Copyright (c) 2011-2013 Butiá Team butia@fing.edu.uy 
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

import time
import threading
import re
import subprocess
import commands
import gconf
from pybot import pybot_client

from TurtleArt.tapalette import special_block_colors
from TurtleArt.tapalette import palette_name_to_index
from TurtleArt.tapalette import make_palette
from TurtleArt.talogo import primitive_dictionary, logoerror
from TurtleArt.tautils import debug_output, power_manager_off
from TurtleArt.tawindow import block_names

from plugins.plugin import Plugin

from gettext import gettext as _

#constants definitions
ERROR = -1   # default return value in case of error
MAX_SPEED = 1023   # max velocity for AX-12 - 10 bits -
MAX_SENSOR_PER_TYPE = 6
COLOR_NOTPRESENT = ["#A0A0A0","#808080"] 
COLOR_PRESENT = ["#00FF00","#008000"]
BATTERY_RED = ["#FF0000","#808080"]
BATTERY_ORANGE = ["#FFA500","#808080"]

ERROR_SPEED = _('ERROR: The speed must be a value between 0 and 1023')
ERROR_SPEED_ABS = _('ERROR: The speed must be a value between -1023 and 1023')
ERROR_PIN_NUMBER = _('ERROR: The pin must be between 1 and 8')
ERROR_PIN_VALUE = _('ERROR: The value must be 0 or 1, LOW or HIGH')
ERROR_PIN_MODE = _('ERROR: The mode must be INPUT or OUTPUT.')

GCONF_CAST = '/desktop/sugar/activities/turtlebots/cast/'

#Dictionary for help string asociated to modules used for automatic generation of block instances
modules_help = {} 
modules_help['led'] = _("turns LED on and off: 1 means on, 0 means off")
modules_help['gray'] = _("returns the gray level as a value between 0 and 65535")
modules_help['button'] = _("returns 1 when the button is pressed and 0 otherwise")
modules_help['light'] = _("returns the light level as a value between 0 and 65535")
modules_help['distance'] = _("returns the distance as a value between 0 and 65535")
modules_help['resistanceB'] = _("returns the resistance value (ohms)")
modules_help['voltageB'] = _("returns the voltage value (volts)")
modules_help['module_a'] = _("custom module A")
modules_help['module_b'] = _("custom module B")
modules_help['module_c'] = _("custom module C")

#Dictionary for translating block name to module name used for automatic generation of block instances
modules_name_from_device_id = {} 
modules_name_from_device_id['led'] = 'led'
modules_name_from_device_id['button'] = 'button'
modules_name_from_device_id['gray'] = 'grey'
modules_name_from_device_id['light'] = 'light'
modules_name_from_device_id['distance'] = 'distanc'
modules_name_from_device_id['resistanceB'] = 'res'
modules_name_from_device_id['voltageB'] = 'volt'
modules_name_from_device_id['module_a'] = 'moduleA'
modules_name_from_device_id['module_b'] = 'moduleB'
modules_name_from_device_id['module_c'] = 'moduleC'

device_id_from_module_name = {} 
device_id_from_module_name['led'] = 'led'
device_id_from_module_name['button'] = 'button'
device_id_from_module_name['grey'] = 'gray'
device_id_from_module_name['light'] = 'light'
device_id_from_module_name['distanc'] = 'distance'
device_id_from_module_name['res'] = 'resistance'
device_id_from_module_name['volt'] = 'voltage'
device_id_from_module_name['moduleA'] = 'module_a'
device_id_from_module_name['moduleB'] = 'module_b'
device_id_from_module_name['moduleC'] = 'module_c'

label_name_from_device_id= {} 
label_name_from_device_id['led'] = _('LED')
label_name_from_device_id['button'] = _('button')
label_name_from_device_id['gray'] = _('gray')
label_name_from_device_id['light'] = _('light')
label_name_from_device_id['distance'] = _('distance')
label_name_from_device_id['resistanceB'] = _('resistance')
label_name_from_device_id['voltageB'] = _('voltage')
label_name_from_device_id['module_a'] = _('module a')
label_name_from_device_id['module_b'] = _('module b')
label_name_from_device_id['module_c'] = _('module c')

refreshable_block_list = ['light', 'gray', 'distance', 'button', 'led', 'resistanceB', 'voltageB', 'module_a', 'module_b', 'module_c']
static_block_list = ['forwardButia', 'backwardButia', 'leftButia', 'rightButia', 'stopButia', 'speedButia', 'batterychargeButia', 'moveButia']
extras_block_list = ['setpinButia', 'getpinButia', 'pinmodeButia', 'highButia', 'lowButia', 'inputButia', 'outputButia', 'const_aButia', 'const_bButia', 'const_cButia']

class Butia(Plugin):
    
    def __init__(self, parent):
        self.tw = parent
        self.gconf_client = gconf.client_get_default()
        power_manager_off(True)
        self.butia = pybot_client.robot(auto_connect=False)
        self.actualSpeed = [600, 600]
        self.hack_states = [1, 1, 1, 1, 1, 1, 1, 1]
        self.pollthread = None
        self.pollrun = True
        self.bobot = None
        self.use_cc = False
        self.m_d = {}
        self.match_dict = {}
        self.battery_value = ERROR
        self.battery_color = COLOR_NOTPRESENT[:]
        self.old_battery_color = COLOR_NOTPRESENT[:]
        self.statics_color = COLOR_NOTPRESENT[:]
        self.extras_color = COLOR_NOTPRESENT[:]
        self.old_extras_color = COLOR_NOTPRESENT[:]
        self.match_list = []
        self.modules_changed = []
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
                     help_string=_('returns the battery charge in volts. If no motors present, it returns 255'))
        self.tw.lc.def_prim('batterychargeButia', 0, lambda self: primitive_dictionary['batterychargeButia']())
        special_block_colors['batterychargeButia'] = COLOR_NOTPRESENT[:]

        primitive_dictionary['speedButia'] = self.speedButia
        palette.add_block('speedButia',
                     style='basic-style-1arg',
                     label=[_('speed Butia')],
                     prim_name='speedButia',
                     default=[600],
                     help_string=_('set the speed of the Butia motors'))
        self.tw.lc.def_prim('speedButia', 1, lambda self, x: primitive_dictionary['speedButia'](x))
        special_block_colors['speedButia'] = COLOR_NOTPRESENT[:]
        
        primitive_dictionary['moveButia'] = self.moveButia
        palette.add_block('moveButia',
                     style='basic-style-2arg',
                     label=[_('move Butia'), _('left'), _('right')],
                     prim_name='moveButia',
                     default=[600, 600],
                     help_string=_('moves the Butia motors at the specified speed'))
        self.tw.lc.def_prim('moveButia', 2, lambda self, x, y: primitive_dictionary['moveButia'](x, y))
        special_block_colors['moveButia'] = COLOR_NOTPRESENT[:]

        primitive_dictionary['stopButia'] = self.stopButia
        palette.add_block('stopButia',
                     style='basic-style',
                     label=_('stop Butia'),
                     prim_name='stopButia',
                     help_string=_('stop the Butia robot'))
        self.tw.lc.def_prim('stopButia', 0, lambda self: primitive_dictionary['stopButia']())
        special_block_colors['stopButia'] = COLOR_NOTPRESENT[:]

        primitive_dictionary['forwardButia'] = self.forwardButia
        palette.add_block('forwardButia',
                     style='basic-style',
                     label=_('forward Butia'),
                     prim_name='forwardButia',
                     help_string=_('move the Butia robot forward'))
        self.tw.lc.def_prim('forwardButia', 0, lambda self: primitive_dictionary['forwardButia']())
        special_block_colors['forwardButia'] = COLOR_NOTPRESENT[:]

        primitive_dictionary['leftButia'] = self.leftButia
        palette.add_block('leftButia',
                     style='basic-style',
                     label=_('left Butia'),
                     prim_name='leftButia',
                     help_string=_('turn the Butia robot at left'))
        self.tw.lc.def_prim('leftButia', 0, lambda self: primitive_dictionary['leftButia']())
        special_block_colors['leftButia'] = COLOR_NOTPRESENT[:]
        
        primitive_dictionary['rightButia'] = self.rightButia
        palette.add_block('rightButia',
                     style='basic-style',
                     label=_('right Butia'),
                     prim_name='rightButia',
                     help_string=_('turn the Butia robot at right'))
        self.tw.lc.def_prim('rightButia', 0, lambda self: primitive_dictionary['rightButia']())
        special_block_colors['rightButia'] = COLOR_NOTPRESENT[:]

        primitive_dictionary['backwardButia'] = self.backwardButia
        palette.add_block('backwardButia',
                     style='basic-style',
                     label=_('backward Butia'),
                     prim_name='backwardButia',
                     help_string=_('move the Butia robot backward'))
        self.tw.lc.def_prim('backwardButia', 0, lambda self: primitive_dictionary['backwardButia']())
        special_block_colors['backwardButia'] = COLOR_NOTPRESENT[:]

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
        special_block_colors['pinmodeButia'] = COLOR_NOTPRESENT[:]

        primitive_dictionary['setpinButia'] = self.setpinButia
        palette2.add_block('setpinButia',
                     style='basic-style-2arg',
                     label=[_('write hack pin Butia'), _('pin'), _('value')],
                     prim_name='setpinButia',
                     default=[1, 0],
                     help_string=_('set a hack pin to 0 or 1'))
        self.tw.lc.def_prim('setpinButia', 2, lambda self, x, y: primitive_dictionary['setpinButia'](x, y))
        special_block_colors['setpinButia'] = COLOR_NOTPRESENT[:]

        primitive_dictionary['getpinButia'] = self.getpinButia
        palette2.add_block('getpinButia',
                     style='number-style-1arg',
                     label=[_('read hack pin Butia')],
                     prim_name='getpinButia',
                     default=1,
                     help_string=_('read the value of a hack pin'))
        self.tw.lc.def_prim('getpinButia', 1, lambda self, x: primitive_dictionary['getpinButia'](x))
        special_block_colors['getpinButia'] = COLOR_NOTPRESENT[:]

        primitive_dictionary['inputButia'] = self.inputButia
        palette2.add_block('inputButia',
                  style='box-style',
                  label=_('INPUT'),
                  help_string=_('Configure hack port for digital input.'),
                  prim_name='inputButia')
        self.tw.lc.def_prim('inputButia', 0, lambda self: primitive_dictionary['inputButia']())
        special_block_colors['inputButia'] = COLOR_NOTPRESENT[:]

        primitive_dictionary['highButia'] = self.highButia
        palette2.add_block('highButia',
                  style='box-style',
                  label=_('HIGH'),
                  help_string=_('Set HIGH value for digital port.'),
                  prim_name='highButia')
        self.tw.lc.def_prim('highButia', 0, lambda self: primitive_dictionary['highButia']())
        special_block_colors['highButia'] = COLOR_NOTPRESENT[:]

        primitive_dictionary['lowButia'] = self.lowButia
        palette2.add_block('lowButia',
                  style='box-style',
                  label=_('LOW'),
                  help_string=_('Set LOW value for digital port.'),
                  prim_name='lowButia')
        self.tw.lc.def_prim('lowButia', 0, lambda self: primitive_dictionary['lowButia']())
        special_block_colors['lowButia'] = COLOR_NOTPRESENT[:]

        primitive_dictionary['outputButia'] = self.outputButia
        palette2.add_block('outputButia',
                  style='box-style',
                  label=_('OUTPUT'),
                  help_string=_('Configure hack port for digital output.'),
                  prim_name='outputButia')
        self.tw.lc.def_prim('outputButia', 0, lambda self: primitive_dictionary['outputButia']())
        special_block_colors['outputButia'] = COLOR_NOTPRESENT[:]

        #add every function in the code 
        primitive_dictionary['ledButia'] = self.ledButia
        primitive_dictionary['lightButia'] = self.lightButia
        primitive_dictionary['grayButia'] = self.grayButia
        primitive_dictionary['buttonButia'] = self.buttonButia
        primitive_dictionary['distanceButia'] = self.distanceButia
        primitive_dictionary['resistanceBButia'] = self.resistanceButia
        primitive_dictionary['voltageBButia'] = self.voltageButia
        primitive_dictionary['module_aButia'] = self.module_aButia
        primitive_dictionary['module_bButia'] = self.module_bButia
        primitive_dictionary['module_cButia'] = self.module_cButia

        #generic mecanism to add sensors that allows multiple instances, depending on the number of instances connected to the 
        #physical robot the corresponding block appears in the pallete

        for j in ['led']:
            for m in range(MAX_SENSOR_PER_TYPE):
                if (m == 0):
                    isHidden = False
                    k = ''
                else:
                    isHidden = True
                    k = m
                module = j + str(k)
                block_name = module + 'Butia'
                palette.add_block(block_name, 
                     style='basic-style-1arg',
                     label=(label_name_from_device_id[j] + str(k) + ' ' +  _('Butia')),
                     prim_name= block_name,
                     default=1,
                     help_string=_(modules_help[j]),
                     hidden=isHidden)
                self.tw.lc.def_prim(block_name, 1, lambda self, w, x=m, y=j, z=0: primitive_dictionary[y + 'Butia'](w, x, z))
                special_block_colors[block_name] = COLOR_NOTPRESENT[:]

        for j in ['button', 'gray', 'light', 'distance', 'resistanceB', 'voltageB', 'module_a', 'module_b', 'module_c']:
            for m in range(MAX_SENSOR_PER_TYPE):
                if (m == 0):
                    isHidden = False
                    k = ''
                else:
                    isHidden = True
                    k = m
                module = j + str(k)
                block_name = module + 'Butia'
                if (j in ['resistanceB', 'voltageB', 'module_a', 'module_b', 'module_c']):
                    pal = palette2
                else:
                    pal = palette
                pal.add_block(block_name, 
                     style='box-style',
                     label=(label_name_from_device_id[j] + str(k) + ' ' +  _('Butia')),
                     prim_name= block_name,
                     help_string=_(modules_help[j]),
                     hidden=isHidden)
                self.tw.lc.def_prim(block_name, 0, lambda self, x=m, y=j, z=0: primitive_dictionary[y + 'Butia'](x, z))
                special_block_colors[block_name] = COLOR_NOTPRESENT[:]

        # const blocks
        primitive_dictionary['castButia'] = self.castButia
        palette2.add_block('castButia',
                  style='basic-style-3arg',
                  label=[_('CAST\n'), _('new name'), _('original'), _('f(x)=')],
                  default=['', '', 'x'],
                  help_string=_('Cast a new block'),
                  prim_name='castButia')
        self.tw.lc.def_prim('castButia', 3, lambda self, x, y, z: primitive_dictionary['castButia'](x, y, z))
        special_block_colors['castButia'] = COLOR_PRESENT[:]

        primitive_dictionary['const_aButia'] = self.const_aButia
        palette2.add_block('const_aButia',
                  style='box-style',
                  label=_('Module A'),
                  help_string=_('generic Module A'),
                  prim_name='const_aButia')
        self.tw.lc.def_prim('const_aButia', 0, lambda self: primitive_dictionary['const_aButia']())
        special_block_colors['const_aButia'] = COLOR_PRESENT[:]

        primitive_dictionary['const_bButia'] = self.const_bButia
        palette2.add_block('const_bButia',
                  style='box-style',
                  label=_('Module B'),
                  help_string=_('generic Module B'),
                  prim_name='const_bButia')
        self.tw.lc.def_prim('const_bButia', 0, lambda self: primitive_dictionary['const_bButia']())
        special_block_colors['const_bButia'] = COLOR_PRESENT[:]

        primitive_dictionary['const_cButia'] = self.const_cButia
        palette2.add_block('const_cButia',
                  style='box-style',
                  label=_('Module C'),
                  help_string=_('generic Module C'),
                  prim_name='const_cButia')
        self.tw.lc.def_prim('const_cButia', 0, lambda self: primitive_dictionary['const_cButia']())
        special_block_colors['const_cButia'] = COLOR_PRESENT[:]



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
        self.butia.closeService()
        self.butia.close()
        if self.bobot:
            self.bobot.kill()
        power_manager_off(False)

    ################################ Refresh process ################################

    def refreshButia(self):
        self.butia.refresh()
        self.check_for_device_change(True)

    def update_colors(self):
        if self.butia.getMotorType() == 2:
            self.use_cc = True
            self.battery_color = BATTERY_ORANGE[:]
            self.statics_color = COLOR_PRESENT[:]
            self.extras_color = None
        else:
            self.use_cc = False
            self.battery_value = self.butia.getBatteryCharge()
            if self.battery_value == ERROR:
                self.battery_color = COLOR_NOTPRESENT[:]
                self.statics_color = COLOR_NOTPRESENT[:]
                self.extras_color = COLOR_NOTPRESENT[:]
            elif (self.battery_value == 255) or (self.battery_value < 7.4):
                self.battery_color = BATTERY_RED[:]
                self.statics_color = COLOR_NOTPRESENT[:]
                self.extras_color = COLOR_PRESENT[:]
            elif (self.battery_value < 254) and (self.battery_value >= 7.4):
                self.battery_color = BATTERY_ORANGE[:]
                self.statics_color = COLOR_PRESENT[:]
                self.extras_color = COLOR_PRESENT[:]

    def block_2_index_and_name(self, block_name):
        """ Splits block_name in name and index, 
        returns a tuple (name,index)
        """
        result = self.regex.search(block_name)
        if result:
            return result.groups()
        else:
            return ('', 0)

    def set_to_list(self, s):
        l = list(s)
        self.modules_changed = []
        for e in l:
            if e[1] in device_id_from_module_name:
                self.modules_changed.append(e[1])

    def make_match_dict(self, l):
        for d in device_id_from_module_name.keys():
            self.m_d[d] = 0
        _list = []
        for t in l:
            module = t[1]
            if module in device_id_from_module_name:
                n = self.m_d[module]
                self.m_d[module] = self.m_d[module] + 1
                if n == 0:
                    _list.append((module, (t[0], t[2])))
                else:
                    _list.append((module + str(n), (t[0], t[2])))
        self.match_dict = dict(_list)

    def change_butia_palette_colors(self, force_refresh, change_statics_blocks, change_extras_blocks, boards_present):

        self.make_match_dict(self.list_connected_device_module)

        for blk in self.tw.block_list.list:
            #NOTE: blocks types: proto, block, trash, deleted
            if (blk.type in ['proto', 'block']) and blk.name.endswith('Butia'):
                if (blk.name in static_block_list):
                    if change_statics_blocks:
                        if (blk.name == 'batterychargeButia'):
                            special_block_colors[blk.name] = self.battery_color[:]
                        else:
                            special_block_colors[blk.name] = self.statics_color[:]
                        if (blk.name == 'moveButia') or (blk.name == 'speedButia') or (blk.name == 'batterychargeButia'):
                            if self.use_cc:
                                blk.set_visibility(False)
                            else:
                                blk.set_visibility(True)
                        blk.refresh()
                elif (blk.name in extras_block_list):
                    if change_extras_blocks:
                        if self.use_cc:
                            blk.set_visibility(False)
                        else:
                            special_block_colors[blk.name] = self.extras_color[:]
                            blk.set_visibility(True)
                        blk.refresh()
                else:
                    blk_name, blk_index = self.block_2_index_and_name(blk.name)
                    if (blk_name in refreshable_block_list):
                        module = modules_name_from_device_id[blk_name]
                        if (module in self.modules_changed) or force_refresh:
                            s = module + blk_index
                            if not(s in self.match_dict):
                                if blk_index !='' :
                                    if blk.type == 'proto': # only make invisible the block in the palette not in the program area
                                        blk.set_visibility(False)
                                    value = str(blk_index)
                                else:
                                    value = '0'
                                print blk_name, module
                                if blk_name in ['module_a', 'module_b', 'module_c']:
                                    label = self.getCastButia(blk_name) + ' ' + _('Butia')
                                else:
                                    label = label_name_from_device_id[blk_name] + ' ' + _('Butia')
                                board = '0'
                                special_block_colors[blk.name] = COLOR_NOTPRESENT[:]
                            else:
                                val = self.match_dict[s]
                                value = val[0]
                                board = val[1]
                                if blk_name in ['module_a', 'module_b', 'module_c']:
                                    label = self.getCastButia(blk_name)
                                else:
                                    label = label_name_from_device_id[blk_name]
                                label = label + ':' + val[0] + ' ' + _('Butia')
                                if boards_present > 1:
                                    label = label + ' ' + val[1]

                                if blk.type == 'proto': # don't has sense to change the visibility of a block in the program area
                                    blk.set_visibility(True)
                                special_block_colors[blk.name] = COLOR_PRESENT[:]

                            if module == 'led':
                                self.tw.lc.def_prim(blk.name, 1, 
                                lambda self, w, x=value, y=blk_name, z=board: primitive_dictionary[y + 'Butia'](w,x,z))
                            else:
                                self.tw.lc.def_prim(blk.name, 0, 
                                lambda self, x=value, y=blk_name, z=board: primitive_dictionary[y+ 'Butia'](x, z))

                            blk.spr.set_label(label)
                            block_names[blk.name][0] = label
                            blk.refresh()

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

    def check_for_device_change(self, force_refresh):
        """ if there exists new devices connected or disconections to the butia IO board, 
         then it change the color of the blocks corresponding to the device """
        
        old_list_connected_device_module = self.list_connected_device_module[:]
        self.list_connected_device_module = self.butia.getModulesList(False)
        boards_present = self.butia.getButiaCount()

        self.update_colors()
        
        if force_refresh:
            self.change_butia_palette_colors(True, True, True, boards_present)
        else:
            if not(old_list_connected_device_module == self.list_connected_device_module):
                set_old_connected_device_module = set(old_list_connected_device_module)
                set_connected_device_module = set(self.list_connected_device_module)
                set_new_device_module = set_connected_device_module.difference(set_old_connected_device_module)
                set_old_device_module = set_old_connected_device_module.difference(set_connected_device_module)
                set_changed_device_module = set_new_device_module.union(set_old_device_module)
                self.set_to_list(set_changed_device_module)
            else:
                self.modules_changed = []

            if not(self.battery_color == self.old_battery_color):
                change_statics_blocks = True
                self.old_battery_color = self.battery_color
            else:
                change_statics_blocks = False

            if not(self.extras_color == self.old_extras_color):
                change_extras_blocks = True
                self.old_extras_color = self.extras_color
            else:
                change_extras_blocks = False

            if not(self.modules_changed == []) or change_statics_blocks or change_extras_blocks:
                self.change_butia_palette_colors(False, change_statics_blocks, change_extras_blocks, boards_present)

    ################################ Movement calls ################################

    def set_vels(self, left, right):
        if left > 0:
            sentLeft = '0'
        else:
            sentLeft = '1'
        if right > 0:
            sentRight = '0'
        else:
            sentRight = '1'
        self.butia.set2MotorSpeed(sentLeft, str(abs(left)), sentRight, str(abs(right)))

    def moveButia(self, left, right):
        try:
            left = int(left)
        except:
            left = 0
        if (left < -MAX_SPEED) or (left > MAX_SPEED):
            raise logoerror(ERROR_SPEED_ABS)
        try:
            right = int(right)
        except:
            right = 0
        if (right < -MAX_SPEED) or (right > MAX_SPEED):
            raise logoerror(ERROR_SPEED_ABS)
        self.set_vels(left, right)

    def forwardButia(self):
        self.set_vels(self.actualSpeed[0], self.actualSpeed[1])

    def backwardButia(self):
        self.set_vels(-self.actualSpeed[0], -self.actualSpeed[1])

    def leftButia(self):
        self.set_vels(-self.actualSpeed[0], self.actualSpeed[1])

    def rightButia(self):
        self.set_vels(self.actualSpeed[0], -self.actualSpeed[1])

    def stopButia(self):
        self.set_vels(0, 0)

    def speedButia(self, speed):
        try:
            speed = int(speed)
        except:
            speed = ERROR
        if (speed < 0) or (speed > MAX_SPEED):
            raise logoerror(ERROR_SPEED)
        self.actualSpeed = [speed, speed]

    ################################ Sensors calls ################################

    def batterychargeButia(self):
        if self.use_cc:
            return 255
        else:
            return self.butia.getBatteryCharge()

    def buttonButia(self, sensorid='0', boardid='0'):
        return self.butia.getButton(sensorid, boardid)

    def lightButia(self, sensorid='0', boardid='0'):
        return self.butia.getLight(sensorid, boardid)

    def distanceButia(self, sensorid='0', boardid='0'):
        return self.butia.getDistance(sensorid, boardid)

    def grayButia(self, sensorid='0', boardid='0'):
        return self.butia.getGray(sensorid, boardid)

    def resistanceButia(self, sensorid='0', boardid='0'):
        return self.butia.getResistance(sensorid, boardid)

    def voltageButia(self, sensorid='0', boardid='0'):
        return self.butia.getVoltage(sensorid, boardid)

    def ledButia(self, value, sensorid='0', boardid='0'):
        try:
            value = int(value)
        except:
            value = ERROR
        if (value < 0) or (value > 1):
            raise logoerror(ERROR_PIN_VALUE)
        else:
            self.butia.setLed(sensorid, value, boardid)

    ################################ Extras ################################

    def pinmodeButia(self, pin, mode):
        if not(self.use_cc):
            try:
                pin = int(pin)
            except:
                pin = ERROR
            if (pin < 1) or (pin > 8):
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

    def highButia(self):
        return 1

    def lowButia(self):
        return 0

    def inputButia(self):
        return _('INPUT')

    def outputButia(self):
        return _('OUTPUT')

    def setpinButia(self, pin, value):
        if not(self.use_cc):
            try:
                pin = int(pin)
            except:
                pin = ERROR
            if (pin < 1) or (pin > 8):
                raise logoerror(ERROR_PIN_NUMBER)
            else:
                if self.hack_states[pin] == 1:
                    raise logoerror(_('ERROR: The pin %s must be in OUTPUT mode.') % pin)
                else:
                    try:
                        value = int(value)
                    except:
                        value = ERROR
                    if (value < 0) or (value > 1):
                        raise logoerror(ERROR_PIN_VALUE)
                    else:
                        self.butia.setHack(pin, value)

    def getpinButia(self, pin):
        if not(self.use_cc):
            try:
                pin = int(pin)
            except:
                pin = ERROR
            if (pin < 1) or (pin > 8):
                raise logoerror(ERROR_PIN_NUMBER)
            else:
                if self.hack_states[pin] == 0:
                    raise logoerror(_('ERROR: The pin %s must be in INPUT mode.') % pin)
                else:
                    return self.butia.getHack(pin)

    ################################ Custom modules ################################

    def const_aButia(self):
        return _('Module A')

    def const_bButia(self):
        return _('Module B')

    def const_cButia(self):
        return _('Module C')

    def module_aButia(self, sensorid=0, boardid=0):
        return self.butia.getModuleA(sensorid, boardid)

    def module_bButia(self, sensorid=0, boardid=0):
        return self.butia.getModuleB(sensorid, boardid)

    def module_cButia(self, sensorid=0, boardid=0):
        return self.butia.getModuleC(sensorid, boardid)

    def getCastButia(self, t):
        if (t == 'module_a'):
            return self.gconf_client.get_string(GCONF_CAST + 'moduleA')
        elif (t == 'module_b'):
            return self.gconf_client.get_string(GCONF_CAST + 'moduleB')
        elif (t == 'module_c'):
            return self.gconf_client.get_string(GCONF_CAST + 'moduleC')
        else:
            print 'wrong cast', t

    def castButia(self, new_name, original, conversion):
        print 'original', original
        print 'new name', new_name
        print 'conv', conversion


        if original == _('Module A'):
            module_block = 'module_a'
            self.gconf_client.set_string(GCONF_CAST + 'moduleA', str(new_name))
        elif original == _('Module B'):
            module_block = 'module_b'
            self.gconf_client.set_string(GCONF_CAST + 'moduleB', str(new_name))
        elif original == _('Module C'):
            module_block = 'module_c'
            self.gconf_client.set_string(GCONF_CAST + 'moduleC', str(new_name))
        else:
            print 'error'

        #refreshable_block_list

        for blk in self.tw.block_list.list:
            if (blk.type in ['proto', 'block']) and blk.name.endswith('Butia'):
                blk_name, blk_index = self.block_2_index_and_name(blk.name)

                if (blk_name == module_block):
                    #print 'adentro', blk_name, blk_index
                    label = new_name + ' ' + _('Butia')

                    if blk.type == 'proto':
                        if blk_index == '0':
                            blk.set_visibility(True)

                    #el refresh lo pone en verde
                    #special_block_colors[blk.name] = COLOR_PRESENT[:]


                    blk.spr.set_label(label)
                    block_names[blk.name][0] = label
                    blk.refresh()

        try:
            index = palette_name_to_index('butia-extra')
            self.tw.regenerate_palette(index)
        except:
            pass

    ################################ pybot and thread ################################

    def pybot_launch(self):
        res = self.butia.reconnect()
        if res == ERROR:
            try:
                debug_output('Creating Pybot server')
                self.bobot = subprocess.Popen(['python', 'pybot_server.py'], cwd='./plugins/butia/pybot')
                time.sleep(1)
                self.butia.reconnect()
            except:
                debug_output('ERROR creating Pybot server')
        else:
            debug_output('A bot is alive!')
        self.pollthread=threading.Timer(1, self.bobot_poll)
        self.pollthread.start()

    def bobot_poll(self):
        if self.pollrun:
            self.pollthread = threading.Timer(6, self.bobot_poll)
            if self.tw.activity.init_complete:
                if self.can_refresh:
                    self.pollthread = threading.Timer(3, self.bobot_poll)
                self.check_for_device_change(False)
            self.pollthread.start()
        else:
            debug_output("Ending butia poll")

