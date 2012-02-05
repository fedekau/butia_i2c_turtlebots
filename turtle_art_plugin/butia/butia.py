# -*- coding: utf-8 -*-
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
from TurtleArt.tapalette import special_block_colors
from TurtleArt.tapalette import palette_name_to_index
from TurtleArt.tapalette import palette_blocks
from TurtleArt.tapalette import make_palette
from TurtleArt.talogo import primitive_dictionary
from TurtleArt.taconstants import BOX_COLORS
from TurtleArt.tautils import debug_output

from gettext import gettext as _

#constants definitions
ERROR_SENSOR_READ = -1   # default return value in case of error when reading a sensor
WAIT_FOR_BOBOT = 4   # waiting trys for bobot-server (the butia robot lua server)
MAX_SPEED = 1023   # max velocity for AX-12 - 10 bits -
MAX_SENSOR_PER_TYPE = 8
COLOR_NOTPRESENT = ["#A0A0A0","#808080"] 
COLOR_PRESENT = ["#00FF00","#008000"] #FIXME change for another tone of gray to avoid confusion with some similar blocks or the turtle
WHEELBASE = 28.00

#Dictionary for help string asociated to modules used for automatic generation of block instances
modules_help = {} 
modules_help['led'] = _("adjust LED intensity between 0 and 255")
modules_help['grayscale'] = _("returns the object gray level encountered him as a number between 0 and 1023")
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
refreshable_modules_list = ['ambientlight', 'grayscale', 'temperature', 'distance', 'button', 'tilt', 'magneticinduction', 'vibration', 'led' ]

static_block_list = ['forwardButia', 'backwardButia', 'leftButia', 'rightButia', 'stopButia', 'speedButia', 'forwardDistance', 
              'backwardDistance', 'turnXdegree', 'LCDdisplayButia'] 

class Butia(gobject.GObject):
    actualSpeed = 600 # velocidad con la que realiza los movimientos forward, backward, left y right
    def __init__(self, parent):
        gobject.GObject.__init__(self)
        self.tw = parent
        self.butia = None
        self.pollthread = None
        #start butia services
        self.bobot_launch()
        self.butia = butiaAPI.robot()
        self.list_connected_devices = []
 
    
    def _check_init(self):
        if self.butia is None:
            debug_output("reinitializing butia ...")
            self.butia = butiaAPI.robot()
            #self.butia.abrirSensor()
            #self.butia.abrirMotores()
        

    def setup(self):
        """ Setup is called once, when the Turtle Window is created. """

        palette = make_palette('butia', colors=COLOR_PRESENT, help_string=_('Butia Robot'))

        #add block about movement of butia, this blocks don't allow multiple instances

        primitive_dictionary['refreshButia'] = self.refreshButia
        palette.add_block('refreshButia',  # the name of your block
                     style='basic-style',  # the block style
                     label=_('Refresh Butia'),  # the label for the block
                     prim_name='refreshButia',  # code reference (see below)
                     help_string=_('Search for a connected Butiá robot'))
        self.tw.lc.def_prim('refreshButia', 0, lambda self : primitive_dictionary['refreshButia']())

        primitive_dictionary['batterychargeButia'] = self.batterychargeButia
        palette.add_block('batterychargeButia',  # the name of your block
                     style='box-style',  # the block style
                     label=_('battery charge Butia'),  # the label for the block
                     prim_name='batterychargeButia',  # code reference (see below)
                     help_string=_('returns the battery charge as a number between 0 and 255'))
        self.tw.lc.def_prim('batterychargeButia', 0, lambda self: primitive_dictionary['batterychargeButia']())

        primitive_dictionary['speedButia'] = self.speedButia
        palette.add_block('speedButia',  # the name of your block
                     style='basic-style-1arg',  # the block style
                     label=_('speed Butia'),  # the label for the block
                     prim_name='speedButia',  # code reference (see below)
                     default=[600],
                     help_string=_('set the speed of the Butia motors as a value between 0 and 1023, passed by an argument'))
        self.tw.lc.def_prim('speedButia', 1, lambda self, x: primitive_dictionary['speedButia'](x))
        
        primitive_dictionary['forwardButia'] = self.forwardButia
        palette.add_block('forwardButia',  # the name of your block
                     style='basic-style',  # the block style
                     label=_('forward Butia'),  # the label for the block
                     prim_name='forwardButia',  # code reference (see below)
                     help_string=_('move the Butia robot forward'))
        self.tw.lc.def_prim('forwardButia', 0, lambda self: primitive_dictionary['forwardButia']())

        primitive_dictionary['forwardDistance'] = self.forwardDistance
        palette.add_block('forwardDistance',  # the name of your block
                     style='basic-style-1arg',  # the block style
                     label=_('forward Butia'),  # the label for the block
                     default=[5],  
                     prim_name='forwardDistance',  # code reference (see below)
                     help_string=_('move the Butia robot forward a predefined distance'))
        self.tw.lc.def_prim('forwardDistance', 1, lambda self, x: primitive_dictionary['forwardDistance'](x))
        
        primitive_dictionary['backwardButia'] = self.backwardButia
        palette.add_block('backwardButia',  # the name of your block
                     style='basic-style',  # the block style
                     label=_('backward Butia'),  # the label for the block
                     prim_name='backwardButia',  # code reference (see below)
                     help_string=_('move the Butia robot backward'))
        self.tw.lc.def_prim('backwardButia', 0, lambda self: primitive_dictionary['backwardButia']())

        primitive_dictionary['backwardDistance'] = self.backwardDistance
        palette.add_block('backwardDistance',  # the name of your block
                     style='basic-style-1arg',  # the block style
                     label=_('backward Butia'),  # the label for the block
                     default=[5],  
                     prim_name='backwardDistance',  # code reference (see below)
                     help_string=_('move the Butia robot backward a predefined distance'))
        self.tw.lc.def_prim('backwardDistance', 1, lambda self, x: primitive_dictionary['backwardDistance'](x))

        primitive_dictionary['leftButia'] = self.leftButia
        palette.add_block('leftButia',  # the name of your block
                     style='basic-style',  # the block style
                     label=_('left Butia'),  # the label for the block
                     prim_name='leftButia',  # code reference (see below)
                     help_string=_('turn the Butia robot at left'))
        self.tw.lc.def_prim('leftButia', 0, lambda self: primitive_dictionary['leftButia']())

        primitive_dictionary['rightButia'] = self.rightButia
        palette.add_block('rightButia',  # the name of your block
                     style='basic-style',  # the block style
                     label=_('right Butia'),  # the label for the block
                     prim_name='rightButia',  # code reference (see below)
                     help_string=_('turn the Butia robot at right'))
        self.tw.lc.def_prim('rightButia', 0, lambda self: primitive_dictionary['rightButia']())

        primitive_dictionary['turnXdegree'] = self.turnXdegree
        palette.add_block('turnXdegree',  # the name of your block
                     style='basic-style-1arg',  # the block style
                     label=_('turn Butia'),  # the label for the block
                     default=[45],  
                     prim_name='turnXdegree',  # code reference (see below)
                     help_string=_('turn the Butia robot x degrees'))
        self.tw.lc.def_prim('turnXdegree', 1, lambda self, x: primitive_dictionary['turnXdegree'](x))

        primitive_dictionary['stopButia'] = self.stopButia
        palette.add_block('stopButia',  # the name of your block
                     style='basic-style',  # the block style
                     label=_('stop Butia'),  # the label for the block
                     prim_name='stopButia',  # code reference (see below)
                     help_string=_('stop the Butia robot'))
        self.tw.lc.def_prim('stopButia', 0, lambda self: primitive_dictionary['stopButia']())

        primitive_dictionary['LCDdisplayButia'] = self.LCDdisplayButia
        palette.add_block('LCDdisplayButia',  # the name of your block
                     style='basic-style-1arg',  # the block style
                     label=_('display Butia'),  # the label for the block
                     default=[_('Hello World    Butia            ')],   
                     prim_name='LCDdisplayButia',  # code reference (see below)
                     help_string=_('print text in Butia robot 32-character ASCII display'))
        self.tw.lc.def_prim('LCDdisplayButia', 1, lambda self, x: primitive_dictionary['LCDdisplayButia'](x))


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


        #generic mecanism to add sensors that allows multiple instances, depending on the number of instances connected to the 
        #physical robot the corresponding block appears in the pallete

        for i in [   ['basic-style-1arg', ['led']],
                     ['box-style', ['button', 'grayscale', 'ambientlight', 'temperature', 'distance', 'tilt', 'magneticinduction', 'vibration']]
                 ]:

            (blockstyle , listofmodules) = i
            for j in listofmodules:
                if blockstyle == 'basic-style-1arg':
                    palette.add_block(j + 'Butia',  # the name of your block
                    style=blockstyle,  # the block style
                    label=(label_name_from_device_id[j] + ' ' + _('Butia')),  # the label for the block
                    prim_name= j + 'Butia',  # code reference (see below)
                    default=[255],
                    help_string=_(modules_help[j]))
                    self.tw.lc.def_prim(j + 'Butia', 1, lambda self, x,y=j: primitive_dictionary[y + 'Butia'](x))
                else:
                    palette.add_block(j + 'Butia',  # the name of your block
                    style=blockstyle,  # the block style
                    label=(label_name_from_device_id[j] + ' ' + _('Butia')),  # the label for the block
                    prim_name= j + 'Butia',  # code reference (see below)
                    help_string=_(modules_help[j]))
                    self.tw.lc.def_prim(j + 'Butia', 0, lambda self, y=j: primitive_dictionary[y + 'Butia']())

                if self.butia.isPresent(modules_name_from_device_id[j]) == False:
                    special_block_colors[j+ 'Butia'] = COLOR_NOTPRESENT

                for k in range(1,MAX_SENSOR_PER_TYPE):
                    module = j + str(k)
                    isHidden = True
                    if self.butia.isPresent(modules_name_from_device_id[j] + str(k)) == True:
                        isHidden = False
                    if blockstyle == 'basic-style-1arg':
                        palette.add_block(module + 'Butia',  # the name of your block 
                                     style=blockstyle,  # the block style
                                     label=( label_name_from_device_id[j] + str(k) + ' ' +  _('Butia')),  # the label for the block
                                     prim_name= module + 'Butia',  # code reference (see below)
                                     help_string=_(modules_help[j]),
                                     default=[255],
                                     hidden=isHidden )
                        self.tw.lc.def_prim(module + 'Butia', 1, lambda self, x, y=k, z=j: primitive_dictionary[z + 'Butia'](x,y))
                    else:
                        palette.add_block(module + 'Butia',  # the name of your block   
                                     style=blockstyle,  # the block style
                                     label=(label_name_from_device_id[j] + str(k) + ' ' + _('Butia')),  # the label for the block
                                     prim_name= module + 'Butia',  # code reference (see below)
                                     help_string=_(modules_help[j]),
                                     hidden=isHidden )
                        self.tw.lc.def_prim(module + 'Butia', 0, lambda self, y=k , z=j: primitive_dictionary[z + 'Butia'](y))
        
        

        #timer to poll butia changes
        self.pollthread=threading.Timer(5,self.bobot_poll)
        self.pollthread.start()
        #self.dynamicLoadBlockColors()

    def start(self):
        #self.tw.show_toolbar_palette(palette_name_to_index('butia'),regenerate=True)
        pass

    def refreshButia(self):
        pass


    def stop(self):
        """ stop is called when stop button is pressed. """

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
        self.pollthread.cancel()
        self.butia.close()
        self.butia.closeService()



    def change_color_blocks(self):
        old_list_connected_devices =  self.list_connected_devices 
        self.list_connected_devices = self.butia.get_modules_list()
        set_old_connected_devices = set(old_list_connected_devices)
        set_connected_devices = set(self.list_connected_devices)
        new_devices = set_connected_devices.difference(set_old_connected_devices)
        old_devices = set_old_connected_devices.difference(set_connected_devices)
        change_devices = new_devices.union(old_devices) # maybe exists one set operation for this
        print 'new devices es:', new_devices
        if change_devices == set([]):
            refresh = False
            print 'no refresco'
        else:
            refresh = True
            print 'refresco'

        if refresh:  # the same with the battery level
            print 'lista modulos cambiados: ', change_devices
            #hack to enable that when you drag the block from the palette to the program mantain the color correspondig with the state, because TB by defect paint in green
            for b in static_block_list:
                if ('butia' in self.list_connected_devices):
                    BOX_COLORS[b] = COLOR_PRESENT[:] 
                else:
                    BOX_COLORS[b] = COLOR_NOTPRESENT[:]
            #endhack
            for blk in self.tw.block_list.list:
                if blk.type in ['proto', 'block']:
                    if blk.name in static_block_list:
                        if ('butia' in self.list_connected_devices):
                            blk.set_colors(COLOR_PRESENT)
                        else:
                            blk.set_colors(COLOR_NOTPRESENT)
                    elif blk.name == 'batterychargeButia':
                        print 'bateria'
                        blk.set_colors(self.batteryColor())

            
            butia_palette_blocks = self.tw.palettes[palette_name_to_index('butia')]
            for j in refreshable_modules_list:        
                module = modules_name_from_device_id[j]
                block_name = j + 'Butia'
                if module in self.list_connected_devices:
                    for b in butia_palette_blocks:
                        if (b.name == block_name):
                            b.set_visibility(True)
                            b.set_colors(COLOR_PRESENT)
                else:
                    for b in butia_palette_blocks:
                        if (b.name == block_name):
                            b.set_colors(COLOR_NOTPRESENT)
                for k in range(1, MAX_SENSOR_PER_TYPE):
                    module = modules_name_from_device_id[j] + str(k)
                    block_name = j + str(k) + 'Butia'
                    if module in self.list_connected_devices:
                        for b in butia_palette_blocks:
                            if (b.name == block_name):
                                b.set_visibility(True)
                                b.set_colors(COLOR_PRESENT)
                    else:
                        for b in butia_palette_blocks:
                            if (b.name == block_name):
                                b.set_colors(COLOR_NOTPRESENT)
                                b.set_visibility(False)

            self.tw.show_toolbar_palette(palette_name_to_index('butia'), regenerate=True, show=False)

    def set_vels(self, left, right):
        self._check_init()
        #print "Setear velocidades: " + str(left) + "-" + str(right)
        if left>0:
                    sentLeft = "0"
        else:
                    sentLeft = "1"
        if right>0:
                    sentRight = "0"
        else:
                    sentRight = "1"
        self.butia.setVelocidadMotores(sentLeft, str(abs(left)), sentRight, str(abs(right)))

    def get_sensor(self, sensor):
        self._check_init()
        sensor = self.butia.getValSenAnalog(str(sensor))
        if sensor == "nil value\n" or sensor == '' or sensor == " " or sensor == None:
                    sensor = ERROR_SENSOR_READ
        return sensor


    def forwardButia(self):
        self._check_init()
        self.set_vels(self.actualSpeed, self.actualSpeed)
        #self.tw.canvas.setpen(True)
        #self.tw.canvas.forward(100)

    def forwardDistance(self, dist):
        self._check_init()
        #FIXME 8.29 para que velocidad? Vel = Dist / Tiempo => Tiempo = Dist / Vel
        tiempo = dist / 8.29
        self.set_vels(self.actualSpeed, self.actualSpeed)
        time.sleep(tiempo)
        self.set_vels(0, 0)
        #FIXME ir avanzando de a poquito en la espera de tiempo y no todo de golpe al final
        self.tw.canvas.setpen(True)
        self.tw.canvas.forward(dist)

    def backwardButia(self):
        self._check_init()
        self.set_vels(-self.actualSpeed, -self.actualSpeed)

    def backwardDistance(self, dist):
        self._check_init()
        #FIXME cambiar el 8.29 por valor que dependa de velocidad
        tiempo = dist / 8.29
        self.set_vels(-self.actualSpeed, -self.actualSpeed)
        time.sleep(tiempo)
        self.tw.canvas.setpen(True)
        self.tw.canvas.forward(-dist)
        self.set_vels(0, 0)

    def leftButia(self):
        self._check_init()
        self.set_vels(self.actualSpeed, -self.actualSpeed)

    def rightButia(self):
        self._check_init()
        self.set_vels(-self.actualSpeed, self.actualSpeed)

    def turnXdegree(self, degrees):
        self._check_init()
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
        self._check_init()
        self.set_vels(0, 0)

    def buttonButia(self, sensorid=''):
        self._check_init()
        return self.butia.getButton(sensorid)

    def batterychargeButia(self):
        self._check_init()
        return int(self.butia.getBatteryCharge())

    def batteryColor(self):
        battery = int(self.butia.getBatteryCharge())
        if (battery == -1) or (battery == 255):
            return COLOR_NOTPRESENT
        elif ((battery < 254) and (battery >= 195)):
            return COLOR_PRESENT
        elif ((battery < 194) and (battery >= 134)):
            return ["#FFFF00","#808080"]
        elif ((battery < 134) and (battery >= 74)):
            return ["#FFA500","#808080"]
        else:
            return ["#FF0000","#808080"]

    def ambientlightButia(self, sensorid=''):
        self._check_init()
        return self.butia.getAmbientLight(sensorid)

    def distanceButia(self, sensorid=''):
        self._check_init()
        return self.butia.getDistance(sensorid)

    def grayscaleButia(self, sensorid=''):
        self._check_init()
        return self.butia.getGrayScale(sensorid)
        
    def temperatureButia(self, sensorid=''):
        self._check_init()
        return self.butia.getTemperature(sensorid)

    def vibrationButia(self, sensorid=''):
        self._check_init()
        return self.butia.getVibration(sensorid)

    def tiltButia(self, sensorid=''):
        self._check_init()
        return self.butia.getTilt(sensorid)

    def capacitivetouchButia(self, sensorid=''):
        self._check_init()
        return self.butia.getCapacitive(sensorid)

    def magneticinductionButia(self, sensorid=''):
        self._check_init()
        return self.butia.getMagneticInduction(sensorid)

    def LCDdisplayButia(self, text='________________________________'):
        self._check_init()
        text = str(text)
        text = text.replace(' ', '_')
        self.butia.llamarModulo('display', 'escribir' , text)

    def ledButia(self, level, sensorid=''):
        self._check_init()
        self.butia.setLed(level)
    
    def speedButia(self, speed):
        #print "Setear velocidad actual: " + str(speed)
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
        cmd = 'ps ax'
        pids = os.popen(cmd)
        x = pids.readlines()
        bobotAlive = False
        for y in x:
            p = y.find('bobot-server')
            if p >= 0: # process running
                bobotAlive = True
                debug_output('bobot is alive!')
                break
            else:                
                bobotAlive = False
        if(bobotAlive==False):
            debug_output('creating bobot')
            cmd = 'cd plugins/butia/butia_support ; ./lua bobot-server.lua &'
            os.system(cmd)

    def bobot_poll(self):
        self.butia.reconnect()
        self.change_color_blocks()
        self.pollthread=threading.Timer(3,self.bobot_poll)
        self.pollthread.start()
        

