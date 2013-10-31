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
import gconf
from pybot import pybot_client

from TurtleArt.tapalette import special_block_colors
from TurtleArt.tapalette import palette_name_to_index
from TurtleArt.tapalette import make_palette
from TurtleArt.talogo import logoerror
from TurtleArt.tautils import debug_output, power_manager_off
from TurtleArt.taconstants import CONSTANTS
from TurtleArt.tawindow import block_names
from TurtleArt.taprimitive import Primitive, ArgSlot, ConstantArg
from TurtleArt.tatype import TYPE_INT, TYPE_FLOAT, TYPE_STRING, TYPE_NUMBER

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

GCONF_CAST = '/desktop/sugar/activities/turtlebots/cast'

#Dictionary for help string asociated to modules used for automatic generation of block instances
modules_help = {} 
modules_help['led'] = _("turns LED on and off: 1 means on, 0 means off")
modules_help['gray'] = _("returns the gray level as a value between 0 and 65535")
modules_help['button'] = _("returns 1 when the button is pressed and 0 otherwise")
modules_help['light'] = _("returns the light level as a value between 0 and 65535")
modules_help['distance'] = _("returns the distance as a value between 0 and 65535")
modules_help['resistanceB'] = _("returns the resistance value (ohms)")
modules_help['voltageB'] = _("returns the voltage value (volts)")
modules_help['temperature'] = _("returns the temperature value (celsius degree)")
modules_help['modSenA'] = _("custom module %s") % _("sensor a")
modules_help['modSenB'] = _("custom module %s") % _("sensor b")
modules_help['modSenC'] = _("custom module %s") % _("sensor c")
modules_help['modActA'] = _("custom module %s") % _("actuator a")
modules_help['modActB'] = _("custom module %s") % _("actuator b")
modules_help['modActC'] = _("custom module %s") % _("actuator c")

#Dictionary for translating block name to module name used for automatic generation of block instances
modules_name_from_device_id = {} 
modules_name_from_device_id['led'] = 'led'
modules_name_from_device_id['button'] = 'button'
modules_name_from_device_id['gray'] = 'grey'
modules_name_from_device_id['light'] = 'light'
modules_name_from_device_id['distance'] = 'distanc'
modules_name_from_device_id['resistanceB'] = 'res'
modules_name_from_device_id['voltageB'] = 'volt'
modules_name_from_device_id['temperature'] = 'temp'
modules_name_from_device_id['modSenA'] = 'modSenA'
modules_name_from_device_id['modSenB'] = 'modSenB'
modules_name_from_device_id['modSenC'] = 'modSenC'
modules_name_from_device_id['modActA'] = 'modActA'
modules_name_from_device_id['modActB'] = 'modActB'
modules_name_from_device_id['modActC'] = 'modActC'

device_id_from_module_name = {} 
device_id_from_module_name['led'] = 'led'
device_id_from_module_name['button'] = 'button'
device_id_from_module_name['grey'] = 'gray'
device_id_from_module_name['light'] = 'light'
device_id_from_module_name['distanc'] = 'distance'
device_id_from_module_name['res'] = 'resistance'
device_id_from_module_name['volt'] = 'voltage'
device_id_from_module_name['temp'] = 'temperature'
device_id_from_module_name['modSenA'] = 'modSenA'
device_id_from_module_name['modSenB'] = 'modSenB'
device_id_from_module_name['modSenC'] = 'modSenC'
device_id_from_module_name['modActA'] = 'modActA'
device_id_from_module_name['modActB'] = 'modActB'
device_id_from_module_name['modActC'] = 'modActC'

label_name_from_device_id= {} 
label_name_from_device_id['led'] = _('LED')
label_name_from_device_id['button'] = _('button')
label_name_from_device_id['gray'] = _('gray')
label_name_from_device_id['light'] = _('light')
label_name_from_device_id['distance'] = _('distance')
label_name_from_device_id['resistanceB'] = _('resistance')
label_name_from_device_id['voltageB'] = _('voltage')
label_name_from_device_id['temperature'] = _('temperature')
label_name_from_device_id['modSenA'] = _('sensor a')
label_name_from_device_id['modSenB'] = _('sensor b')
label_name_from_device_id['modSenC'] = _('sensor c')
label_name_from_device_id['modActA'] = _('actuator a')
label_name_from_device_id['modActB'] = _('actuator b')
label_name_from_device_id['modActC'] = _('actuator c')

#dict of every function in the code
d = {}

refreshable_block_list = ['light', 'gray', 'distance', 'button', 'led', 'resistanceB', 'voltageB', 'temperature', 'modSenA', 'modSenB', 'modSenC', 'modActA', 'modActB', 'modActC']
static_block_list = ['forwardButia', 'backwardButia', 'leftButia', 'rightButia', 'stopButia', 'speedButia', 'batterychargeButia', 'moveButia']
extras_block_list = ['setpinButia', 'getpinButia', 'pinmodeButia', 'highButia', 'lowButia', 'inputButia', 'outputButia']

class Butia(Plugin):
    
    def __init__(self, parent):
        self.tw = parent
        self.init_gconf()
        power_manager_off(True)
        self.flagCIP = True
        self.butia = pybot_client.robot(auto_connect=False)
        self.actualSpeed = [600, 600]
        self.hack_states = [1, 1, 1, 1, 1, 1, 1, 1]
        self.pollthread = None
        self.pollrun = True
        self.bobot = None
        self.use_cc = False
        self.modsen_a_f = 'x'
        self.modsen_b_f = 'x'
        self.modsen_c_f = 'x'
        self.getCastButia()
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
        global d
        d['ledButia'] = self.ledButia
        d['lightButia'] = self.lightButia
        d['grayButia'] = self.grayButia
        d['buttonButia'] = self.buttonButia
        d['distanceButia'] = self.distanceButia
        d['resistanceBButia'] = self.resistanceButia
        d['voltageBButia'] = self.voltageButia
        d['temperatureButia'] = self.temperatureButia
        d['modSenAButia'] = self.modSenAButia
        d['modSenBButia'] = self.modSenBButia
        d['modSenCButia'] = self.modSenCButia
        d['modActAButia'] = self.modActAButia
        d['modActBButia'] = self.modActBButia
        d['modActCButia'] = self.modActCButia

    def setup(self):
        """ Setup is called once, when the Turtle Window is created. """
        debug_output('creating %s palette' % _('butia'), self.tw.running_sugar)
        palette = make_palette('butia', COLOR_NOTPRESENT, _('Butia Robot'), init_on_start=True)

        #add block about movement of butia, this blocks don't allow multiple instances

        palette.add_block('refreshButia',
                     style='basic-style',
                     label=_('refresh Butia'),
                     prim_name='refreshButia',
                     help_string=_('refresh the state of the Butia palette and blocks'))
        self.tw.lc.def_prim('refreshButia', 0,
            Primitive(self.refreshButia))
        special_block_colors['refreshButia'] = COLOR_PRESENT[:]

        palette.add_block('batterychargeButia',
                     style='box-style',
                     label=_('battery charge Butia'),
                     prim_name='batterychargeButia',
                     help_string=_('returns the battery charge in volts. If no motors present, it returns 255'))
        self.tw.lc.def_prim('batterychargeButia', 0,
            Primitive(self.batterychargeButia, TYPE_FLOAT))
        special_block_colors['batterychargeButia'] = COLOR_NOTPRESENT[:]

        palette.add_block('speedButia',
                     style='basic-style-1arg',
                     label=[_('speed Butia')],
                     prim_name='speedButia',
                     default=[600],
                     help_string=_('set the speed of the Butia motors'))
        self.tw.lc.def_prim('speedButia', 1,
            Primitive(self.speedButia, arg_descs=[ArgSlot(TYPE_NUMBER)]))
        special_block_colors['speedButia'] = COLOR_NOTPRESENT[:]
        
        palette.add_block('moveButia',
                     style='basic-style-2arg',
                     label=[_('move Butia'), _('left'), _('right')],
                     prim_name='moveButia',
                     default=[600, 600],
                     help_string=_('moves the Butia motors at the specified speed'))
        self.tw.lc.def_prim('moveButia', 2,
            Primitive(self.moveButia, arg_descs=[ArgSlot(TYPE_NUMBER), ArgSlot(TYPE_NUMBER)]))
        special_block_colors['moveButia'] = COLOR_NOTPRESENT[:]

        palette.add_block('stopButia',
                     style='basic-style',
                     label=_('stop Butia'),
                     prim_name='stopButia',
                     help_string=_('stop the Butia robot'))
        self.tw.lc.def_prim('stopButia', 0, Primitive(self.stopButia))
        special_block_colors['stopButia'] = COLOR_NOTPRESENT[:]

        palette.add_block('forwardButia',
                     style='basic-style',
                     label=_('forward Butia'),
                     prim_name='forwardButia',
                     help_string=_('move the Butia robot forward'))
        self.tw.lc.def_prim('forwardButia', 0, Primitive(self.forwardButia))
        special_block_colors['forwardButia'] = COLOR_NOTPRESENT[:]

        palette.add_block('leftButia',
                     style='basic-style',
                     label=_('left Butia'),
                     prim_name='leftButia',
                     help_string=_('turn the Butia robot at left'))
        self.tw.lc.def_prim('leftButia', 0, Primitive(self.leftButia))
        special_block_colors['leftButia'] = COLOR_NOTPRESENT[:]
        
        palette.add_block('rightButia',
                     style='basic-style',
                     label=_('right Butia'),
                     prim_name='rightButia',
                     help_string=_('turn the Butia robot at right'))
        self.tw.lc.def_prim('rightButia', 0, Primitive(self.rightButia))
        special_block_colors['rightButia'] = COLOR_NOTPRESENT[:]

        palette.add_block('backwardButia',
                     style='basic-style',
                     label=_('backward Butia'),
                     prim_name='backwardButia',
                     help_string=_('move the Butia robot backward'))
        self.tw.lc.def_prim('backwardButia', 0, Primitive(self.backwardButia))
        special_block_colors['backwardButia'] = COLOR_NOTPRESENT[:]

        # Extra palette
        debug_output('creating %s palette' % _('butia-extra'), self.tw.running_sugar)
        palette2 = make_palette('butia-extra', COLOR_NOTPRESENT, _('Butia Robot extra blocks'), init_on_start=True)

        palette2.add_block('pinmodeButia',
                  style='basic-style-2arg',
                  label=[_('pin mode Butia'),_('pin'),_('mode')],
                  help_string=_('Select the pin function (INPUT, OUTPUT).'),
                  default=[1],
                  prim_name='pinmodeButia')
        self.tw.lc.def_prim('pinmodeButia', 2,
            Primitive(self.pinmodeButia, arg_descs=[ArgSlot(TYPE_NUMBER), ArgSlot(TYPE_STRING)]))
        special_block_colors['pinmodeButia'] = COLOR_NOTPRESENT[:]

        palette2.add_block('getpinButia',
                     style='number-style-1arg',
                     label=[_('read pin Butia')],
                     prim_name='getpinButia',
                     default=1,
                     help_string=_('read the value of a pin'))
        self.tw.lc.def_prim('getpinButia', 1,
            Primitive(self.getpinButia, TYPE_INT, [ArgSlot(TYPE_NUMBER)]))
        special_block_colors['getpinButia'] = COLOR_NOTPRESENT[:]

        palette2.add_block('setpinButia',
                     style='basic-style-2arg',
                     label=[_('write pin Butia'), _('pin'), _('value')],
                     prim_name='setpinButia',
                     default=[1, 0],
                     help_string=_('set a hack pin to 0 or 1'))
        self.tw.lc.def_prim('setpinButia', 2,
            Primitive(self.setpinButia, arg_descs=[ArgSlot(TYPE_NUMBER), ArgSlot(TYPE_NUMBER)]))
        special_block_colors['setpinButia'] = COLOR_NOTPRESENT[:]

        global CONSTANTS
        CONSTANTS['INPUT'] = _('INPUT')
        palette2.add_block('inputButia',
                  style='box-style',
                  label=_('INPUT'),
                  help_string=_('Configure hack pin for digital input.'),
                  prim_name='inputButia')
        self.tw.lc.def_prim('inputButia', 0,
            Primitive(CONSTANTS.get, TYPE_STRING, [ConstantArg('INPUT')]))
        special_block_colors['inputButia'] = COLOR_NOTPRESENT[:]

        CONSTANTS['HIGH'] = 1
        palette2.add_block('highButia',
                  style='box-style',
                  label=_('HIGH'),
                  help_string=_('Set HIGH value for digital pin.'),
                  prim_name='highButia')
        self.tw.lc.def_prim('highButia', 0,
            Primitive(CONSTANTS.get, TYPE_STRING, [ConstantArg('HIGH')]))
        special_block_colors['highButia'] = COLOR_NOTPRESENT[:]

        CONSTANTS['LOW'] = 0
        palette2.add_block('lowButia',
                  style='box-style',
                  label=_('LOW'),
                  help_string=_('Set LOW value for digital port.'),
                  prim_name='lowButia')
        self.tw.lc.def_prim('lowButia', 0,
            Primitive(CONSTANTS.get, TYPE_STRING, [ConstantArg('LOW')]))
        special_block_colors['lowButia'] = COLOR_NOTPRESENT[:]

        CONSTANTS['OUTPUT'] = _('OUTPUT')
        palette2.add_block('outputButia',
                  style='box-style',
                  label=_('OUTPUT'),
                  help_string=_('Configure hack port for digital output.'),
                  prim_name='outputButia')
        self.tw.lc.def_prim('outputButia', 0,
            Primitive(CONSTANTS.get, TYPE_STRING, [ConstantArg('OUTPUT')]))
        special_block_colors['outputButia'] = COLOR_NOTPRESENT[:]

        # Cast palette
        debug_output('creating %s palette' % _('butia-cast'), self.tw.running_sugar)
        palette3 = make_palette('butia-cast', COLOR_NOTPRESENT, _('Butia Robot cast blocks'), init_on_start=True)

        #generic mecanism to add sensors that allows multiple instances, depending on the number of instances connected to the 
        #physical robot the corresponding block appears in the pallete

        for j in ['led', 'modActA', 'modActB', 'modActC']:
            if (j in ['modActA', 'modActB', 'modActC']):
                pal = palette3
            else:
                pal = palette
            for m in range(MAX_SENSOR_PER_TYPE):
                if (m == 0):
                    isHidden = False
                    k = ''
                else:
                    isHidden = True
                    k = m
                module = j + str(k)
                block_name = module + 'Butia'
                pal.add_block(block_name, 
                     style='basic-style-1arg',
                     label=(label_name_from_device_id[j] + str(k) + ' ' +  _('Butia')),
                     prim_name= block_name,
                     default=1,
                     help_string=_(modules_help[j]),
                     hidden=isHidden)
                self.tw.lc.def_prim(block_name, 1,
                    Primitive(d[j + 'Butia'], arg_descs=[ArgSlot(TYPE_NUMBER), ConstantArg(k)]))
                special_block_colors[block_name] = COLOR_NOTPRESENT[:]

        for j in ['button', 'gray', 'light', 'distance', 'resistanceB', 'voltageB', 'temperature', 'modSenA', 'modSenB', 'modSenC']:
            if (j in ['resistanceB', 'voltageB', 'temperature']):
                pal = palette2
            elif (j in ['modSenA', 'modSenB', 'modSenC']):
                pal = palette3
            else:
                pal = palette
            for m in range(MAX_SENSOR_PER_TYPE):
                if (m == 0):
                    isHidden = False
                    k = ''
                else:
                    isHidden = True
                    k = m
                module = j + str(k)
                block_name = module + 'Butia'
                
                label = label_name_from_device_id[j] + str(k)

                pal.add_block(block_name, 
                     style='box-style',
                     label=(label + ' ' +  _('Butia')),
                     prim_name= block_name,
                     help_string=_(modules_help[j]),
                     hidden=isHidden)
                self.tw.lc.def_prim(block_name, 0,
                    Primitive(d[j + 'Butia'], TYPE_INT, [ConstantArg(k)]))
                special_block_colors[block_name] = COLOR_NOTPRESENT[:]

        # cast blocks
        palette3.add_block('castButia',
                  style='basic-style-3arg',
                  label=[_('CAST\n'), _('new name'), _('original'), _('f(x)=')],
                  default=[_('name'), '', 'x'],
                  help_string=_('Cast a new block'),
                  prim_name='castButia')
        self.tw.lc.def_prim('castButia', 3,
            Primitive(self.castButia, arg_descs=[ArgSlot(TYPE_STRING), ArgSlot(TYPE_STRING), ArgSlot(TYPE_STRING)]))
        special_block_colors['castButia'] = COLOR_PRESENT[:]

        # const of sensors
        CONSTANTS['sensor a'] = _('sensor a')
        palette3.add_block('const_sen_aButia',
                  style='box-style',
                  label=_('sensor a'),
                  help_string=_('generic module %s') % _('sensor a'),
                  prim_name='const_sen_aButia')
        self.tw.lc.def_prim('const_sen_aButia', 0,
            Primitive(CONSTANTS.get, TYPE_STRING, [ConstantArg('sensor a')]))
        special_block_colors['const_sen_aButia'] = COLOR_PRESENT[:]

        CONSTANTS['sensor b'] = _('sensor b')
        palette3.add_block('const_sen_bButia',
                  style='box-style',
                  label=_('sensor b'),
                  help_string=_('generic module %s') % _('sensor b'),
                  prim_name='const_sen_bButia')
        self.tw.lc.def_prim('const_sen_bButia', 0,
            Primitive(CONSTANTS.get, TYPE_STRING, [ConstantArg('sensor b')]))
        special_block_colors['const_sen_bButia'] = COLOR_PRESENT[:]

        CONSTANTS['sensor c'] = _('sensor c')
        palette3.add_block('const_sen_cButia',
                  style='box-style',
                  label=_('sensor c'),
                  help_string=_('generic module %s') % _('sensor c'),
                  prim_name='const_sen_cButia')
        self.tw.lc.def_prim('const_sen_cButia', 0,
            Primitive(CONSTANTS.get, TYPE_STRING, [ConstantArg('sensor c')]))
        special_block_colors['const_sen_cButia'] = COLOR_PRESENT[:]

        # const of actuators
        CONSTANTS['actuator a'] = _('actuator a')
        palette3.add_block('const_act_aButia',
                  style='box-style',
                  label=_('actuator a'),
                  help_string=_('generic module %s') % _('actuator a'),
                  prim_name='const_act_aButia')
        self.tw.lc.def_prim('const_act_aButia', 0,
            Primitive(CONSTANTS.get, TYPE_STRING, [ConstantArg('actuator a')]))
        special_block_colors['const_act_aButia'] = COLOR_PRESENT[:]

        CONSTANTS['actuator b'] = _('actuator b')
        palette3.add_block('const_act_bButia',
                  style='box-style',
                  label=_('actuator b'),
                  help_string=_('generic module %s') % _('actuator b'),
                  prim_name='const_act_bButia')
        self.tw.lc.def_prim('const_act_bButia', 0,
            Primitive(CONSTANTS.get, TYPE_STRING, [ConstantArg('actuator b')]))
        special_block_colors['const_act_bButia'] = COLOR_PRESENT[:]

        CONSTANTS['actuator c'] = _('actuator c')
        palette3.add_block('const_act_cButia',
                  style='box-style',
                  label=_('actuator c'),
                  help_string=_('generic module %s') % _('actuator c'),
                  prim_name='const_act_cButia')
        self.tw.lc.def_prim('const_act_cButia', 0,
            Primitive(CONSTANTS.get, TYPE_STRING, [ConstantArg('actuator c')]))
        special_block_colors['const_act_cButia'] = COLOR_PRESENT[:]

        palette3.add_block('changeIpButia',
                        style='basic-style-1arg',
                        label=_('Butia IP'),
                        default='localhost',
                        help_string=_('change the ip of butia robot'),
                        prim_name='changeIpButia')
        self.tw.lc.def_prim('changeIpButia', 1,
            Primitive(self.prim_change_ipButia, arg_descs=[ArgSlot(TYPE_STRING)]))
        special_block_colors['changeIpButia'] = COLOR_PRESENT[:]

    ################################ Turtle calls ################################

    def start(self):
        self.can_refresh = False

    def stop(self):
        self.set_vels(0, 0)
        self.can_refresh = True

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
            t = self.butia._split_module(e)
            if t[1] in device_id_from_module_name:
                self.modules_changed.append(t[1])

    def make_match_dict(self):
        for d in device_id_from_module_name.keys():
            self.m_d[d] = 0
        _list = []
        for m in self.list_connected_device_module:
            t = self.butia._split_module(m)
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

        self.make_match_dict()

        self.getCastButia()

        for blk in self.tw.block_list.list:
            #NOTE: blocks types: proto, block, trash, deleted
            if (blk.type in ['proto', 'block']) and blk.name.endswith('Butia'):
                if (blk.name in static_block_list):
                    if change_statics_blocks:
                        if (blk.name == 'batterychargeButia'):
                            special_block_colors[blk.name] = self.battery_color[:]
                        else:
                            special_block_colors[blk.name] = self.statics_color[:]
                        if (blk.name == 'speedButia') or (blk.name == 'batterychargeButia'):
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

                            label = label_name_from_device_id[blk_name]

                            if not(s in self.match_dict):
                                if blk_index !='' :
                                    if blk.type == 'proto': # only make invisible the block in the palette not in the program area
                                        blk.set_visibility(False)
                                    value = str(blk_index)
                                else:
                                    value = '0'
                                label = label + ' ' + _('Butia')
                                board = '0'
                                special_block_colors[blk.name] = COLOR_NOTPRESENT[:]
                            else:
                                val = self.match_dict[s]
                                value = val[0]
                                board = val[1]
                                label = label + ':' + val[0] + ' ' + _('Butia')
                                if boards_present > 1:
                                    label = label + ' ' + val[1]
                                if blk.type == 'proto': # don't has sense to change the visibility of a block in the program area
                                    blk.set_visibility(True)
                                special_block_colors[blk.name] = COLOR_PRESENT[:]

                            if module in ['led', 'modActA', 'modActB', 'modActC']:
                                self.tw.lc.def_prim(blk.name, 1,
                                    Primitive(d[blk_name + 'Butia'], arg_descs=[ArgSlot(TYPE_NUMBER), ConstantArg(value), ConstantArg(board)]))
                            else:
                                self.tw.lc.def_prim(blk.name, 0,
                                    Primitive(d[blk_name + 'Butia'], return_type=TYPE_INT, arg_descs=[ConstantArg(value), ConstantArg(board)]))

                            blk.spr.set_label(label)
                            block_names[blk.name][0] = label
                            blk.refresh()

        try:
            index = palette_name_to_index('butia')
            if index is not None:
                self.tw.regenerate_palette(index)
        except:
            pass

        try:
            index = palette_name_to_index('butia-extra')
            if index is not None:
                self.tw.regenerate_palette(index)
        except:
            pass

        try:
            index = palette_name_to_index('butia-cast')
            if index is not None:
                self.tw.regenerate_palette(index)
        except:
            pass

    def check_for_device_change(self, force_refresh):
        """ if there exists new devices connected or disconections to the butia IO board, 
         then it change the color of the blocks corresponding to the device """
        
        old_list_connected_device_module = self.list_connected_device_module[:]
        self.list_connected_device_module = self.butia.getModulesList()
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

    def buttonButia(self, port='0', board='0'):
        return self.butia.getButton(port, board)

    def lightButia(self, port='0', board='0'):
        return self.butia.getLight(port, board)

    def distanceButia(self, port='0', board='0'):
        return self.butia.getDistance(port, board)

    def grayButia(self, port='0', board='0'):
        return self.butia.getGray(port, board)

    def resistanceButia(self, port='0', board='0'):
        return self.butia.getResistance(port, board)

    def voltageButia(self, port='0', board='0'):
        return self.butia.getVoltage(port, board)

    def temperatureButia(self, port='0', board='0'):
        return self.butia.getTemperature(port, board)

    def ledButia(self, value, port='0', board='0'):
        try:
            value = int(value)
        except:
            value = ERROR
        if (value < 0) or (value > 1):
            raise logoerror(ERROR_PIN_VALUE)
        else:
            self.butia.setLed(port, value, board)

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

    def modSenAButia(self, sensorid=0, boardid=0):
        x = self.butia.getModuleA(sensorid, boardid)
        if x == ERROR:
            return ERROR
        try:
            return eval(self.modsen_a_f)
        except:
            raise logoerror(_("ERROR: Something wrong with function '%s'") % self.modsen_a_f)

    def modSenBButia(self, sensorid=0, boardid=0):
        x = self.butia.getModuleB(sensorid, boardid)
        if x == ERROR:
            return ERROR
        try:
            return eval(self.modsen_b_f)
        except:
            raise logoerror(_("ERROR: Something wrong with function '%s'") % self.modsen_b_f)

    def modSenCButia(self, sensorid=0, boardid=0):
        x = self.butia.getModuleC(sensorid, boardid)
        if x == ERROR:
            return ERROR
        try:
            return eval(self.modsen_c_f)
        except:
            raise logoerror(_("ERROR: Something wrong with function '%s'") % self.modsen_c_f)

    def modActAButia(self, value, sensorid=0, boardid=0):
        self.butia.setModuleA(sensorid, value, boardid)

    def modActBButia(self, value, sensorid=0, boardid=0):
        self.butia.setModuleB(sensorid, value, boardid)

    def modActCButia(self, value, sensorid=0, boardid=0):
        self.butia.setModuleC(sensorid, value, boardid)

    def init_gconf(self):
        try:
            self.gconf_client = gconf.client_get_default()
        except Exception, err:
            debug_output(_('ERROR: cannot init GCONF client: %s') % err)
            self.gconf_client = None
            print err

    def get_gconf(self, key):
        try:
            res = self.gconf_client.get_string(key)
        except:
            return None
        return res

    def set_gconf(self, key, value):
        try:
            self.gconf_client.set_string(key, value)
        except:
            pass

    def getCastButia(self):
        global label_name_from_device_id
        # sensors
        res = self.get_gconf(GCONF_CAST + 'modSenA')
        if res == None:
            res = _('sensor a')
        label_name_from_device_id['modSenA'] = res
        res = self.get_gconf(GCONF_CAST + 'modSenA_f')
        if res == None:
            res = 'x'
        self.modsen_a_f = res

        res = self.get_gconf(GCONF_CAST + 'modSenB')
        if res == None:
            res = _('sensor b')
        label_name_from_device_id['modSenB'] = res
        res = self.get_gconf(GCONF_CAST + 'modSenB_f')
        if res == None:
            res = 'x'
        self.modsen_b_f = res

        res = self.get_gconf(GCONF_CAST + 'modSenC')
        if res == None:
            res = _('sensor c')
        label_name_from_device_id['modSenC'] = res
        res = self.get_gconf(GCONF_CAST + 'modSenC_f')
        if res == None:
            res = 'x'
        self.modsen_c_f = res

        # actuators
        res = self.get_gconf(GCONF_CAST + 'modActA')
        if res == None:
            res = _('actuator a')
        label_name_from_device_id['modActA'] = res

        res = self.get_gconf(GCONF_CAST + 'modActB')
        if res == None:
            res = _('actuator b')
        label_name_from_device_id['modActB'] = res

        res = self.get_gconf(GCONF_CAST + 'modActC')
        if res == None:
            res = _('actuator c')
        label_name_from_device_id['modActC'] = res

    def castButia(self, new_name, original, function):
        global label_name_from_device_id
        new_name = str(new_name)
        function = str(function)
        
        if original == _('sensor a'):
            module_block = 'modSenA'
            self.set_gconf(GCONF_CAST + 'modSenA_f', function)
            self.modsen_a_f = function
        elif original == _('sensor b'):
            module_block = 'modSenB'
            self.set_gconf(GCONF_CAST + 'modSenB_f', function)
            self.modsen_b_f = function
        elif original == _('sensor c'):
            module_block = 'modSenB'
            self.set_gconf(GCONF_CAST + 'modSenC_f', function)
            self.modsen_c_f = function
        elif original == _('actuator a'):
            module_block = 'modActA'
        elif original == _('actuator b'):
            module_block = 'modActB'
        elif original == _('actuator c'):
            module_block = 'modActC'
        else:
            raise logoerror(_('ERROR: You must cast Sensor or Actuator: A, B or C'))

        self.set_gconf(GCONF_CAST + module_block, new_name)
        label_name_from_device_id[module_block] = new_name

        for blk in self.tw.block_list.list:
            if (blk.type in ['proto', 'block']) and blk.name.endswith('Butia'):
                blk_name, blk_index = self.block_2_index_and_name(blk.name)
                if (blk_name == module_block):
                    label = new_name + ' ' + _('Butia')
                    if blk.type == 'proto':
                        if blk_index == '0':
                            blk.set_visibility(True)
                    blk.spr.set_label(label)
                    block_names[blk.name][0] = label
                    blk.refresh()
        try:
            index = palette_name_to_index('butia-cast')
            self.tw.regenerate_palette(index)
        except:
            pass

        #TODO: pensar algo mejor
        self.list_connected_device_module = []

    def prim_change_ipButia(self, ip):
        ip = ip.strip()
        if self._validate_ip(ip):
            self.flagCIP = False
            self.butia = pybot_client.robot(host=ip)
            self.flagCIP = True
        else:
            raise logoerror(_("ERROR: Invalid IP '%s'") % ip)

    def _validate_ip(self, ip):
        if ip == 'localhost':
            return True
        parts = ip.split('.')
        return len(parts) == 4 and all(0 <= int(part) < 256 for part in parts)

    ################################ pybot and thread ################################

    def pybot_launch(self):
        res = self.butia.reconnect()
        if res == ERROR:
            try:
                debug_output(_('Creating PyBot server'))
                self.bobot = subprocess.Popen(['python', 'pybot_server.py'], cwd='./plugins/butia/pybot')
                time.sleep(1)
                self.butia.reconnect()
            except:
                debug_output(_('ERROR creating PyBot server'))
        else:
            debug_output(_('PyBot is alive!'))
        self.pollthread=threading.Timer(1, self.bobot_poll)
        self.pollthread.start()

    def bobot_poll(self):
        if self.pollrun:
            self.pollthread = threading.Timer(6, self.bobot_poll)
            if self.flagCIP and self.tw.activity.init_complete:
                if self.can_refresh:
                    self.pollthread = threading.Timer(3, self.bobot_poll)
                self.check_for_device_change(False)
            self.pollthread.start()
        else:
            debug_output(_("Ending butia polling"))

