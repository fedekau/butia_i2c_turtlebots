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


import apiSumoUY
import math

from TurtleArt.tapalette import make_palette
from TurtleArt.talogo import primitive_dictionary
from TurtleArt.tautils import debug_output

from gettext import gettext as _

from plugins.plugin import Plugin
   
class Sumtia(Plugin):
    
    def __init__(self, parent):
        Plugin.__init__(self)
        self.tw = parent
        self.vel = 10
        self.api = apiSumoUY.apiSumoUY()
        self.api.setPuertos()
        self.api.conectarse() 

    def setup(self):        

        """ Setup is called once, when the Turtle Window is created. """     
        debug_output('creating %s palette' % _('sumtia'), self.tw.running_sugar)
        palette = make_palette('sumtia', ["#00FF00","#008000"], _('SumBot'))

        primitive_dictionary['sendVelocities'] = self.sendVelocities
        palette.add_block('sendVelocities',
                     style='basic-style-2arg',
                     label=_('speed SumBot'),
                     prim_name='sendVelocities',
                     default=[10,10],
                     help_string=_('submit the speed to the SumBot'))
        self.tw.lc.def_prim('sendVelocities', 2, lambda self, x, y: primitive_dictionary['sendVelocities'](x, y))

        primitive_dictionary['setVel'] = self.setVel
        palette.add_block('setVel',
                     style='basic-style-1arg',
                     label=_('speed SumBot'),
                     prim_name='setVel',
                     default=[10],
                     help_string=_('set the default speed for the movement commands'))
        self.tw.lc.def_prim('setVel', 1, lambda self, x: primitive_dictionary['setVel'](x))

        primitive_dictionary['forwardSumtia'] = self.forwardSumtia
        palette.add_block('forwardSumtia',
                     style='basic-style',
                     label=_('forward SumBot'),
                     prim_name='forwardSumtia',
                     help_string=_('move SumBot forward'))
        self.tw.lc.def_prim('forwardSumtia', 0, lambda self: primitive_dictionary['forwardSumtia']())

        primitive_dictionary['backward'] = self.backward
        palette.add_block('backward',
                     style='basic-style',
                     label=_('backward SumBot'),
                     prim_name='backward',
                     help_string=_('move SumBot backward'))
        self.tw.lc.def_prim('backward', 0, lambda self: primitive_dictionary['backward']())
        
        primitive_dictionary['stopSumtia'] = self.stopSumtia
        palette.add_block('stopSumtia',
                     style='basic-style',
                     label=_('stop SumBot'),
                     prim_name='stopSumtia',
                     help_string=_('stop the SumBot'))
        self.tw.lc.def_prim('stopSumtia', 0, lambda self: primitive_dictionary['stopSumtia']())

        primitive_dictionary['turnLeft'] = self.turnLeft
        palette.add_block('turnLeft',
                     style='basic-style',
                     label=_('left SumBot'),
                     prim_name='turnLeft',
                     help_string=_('turn left the SumBot'))
        self.tw.lc.def_prim('turnLeft', 0, lambda self: primitive_dictionary['turnLeft']())

        primitive_dictionary['turnRight'] = self.turnRight
        palette.add_block('turnRight',
                     style='basic-style',
                     label=_('right SumBot'),
                     prim_name='turnRight',
                     help_string=_('turn right the SumBot'))
        self.tw.lc.def_prim('turnRight', 0, lambda self: primitive_dictionary['turnRight']())

        primitive_dictionary['angleToCenter'] = self.angleToCenter
        palette.add_block('angleToCenter',
                     style='box-style',
                     label=_('angle to center'),
                     prim_name='angleToCenter',
                     help_string=_('get the angle to the center of the dohyo'))
        self.tw.lc.def_prim('angleToCenter', 0, lambda self: primitive_dictionary['angleToCenter']())

        primitive_dictionary['angleToOpponent'] = self.angleToOpponent
        palette.add_block('angleToOpponent',
                     style='box-style',
                     label=_('angle to Enemy'),
                     prim_name='angleToOpponent',
                     help_string=_('get the angle to the Enemy'))
        self.tw.lc.def_prim('angleToOpponent', 0, lambda self: primitive_dictionary['angleToOpponent']())
        
        primitive_dictionary['getX'] = self.getX
        palette.add_block('getX',
                     style='box-style',
                     label=_('x coor. SumBot'),
                     prim_name='getX',
                     help_string=_('get the x coordinate of the SumBot'))
        self.tw.lc.def_prim('getX', 0, lambda self: primitive_dictionary['getX']())
        
        primitive_dictionary['getY'] = self.getY
        palette.add_block('getY',
                     style='box-style',
                     label=_('y coor. SumBot'),
                     prim_name='getY',
                     help_string=_('get the y coordinate of the SumBot'))
        self.tw.lc.def_prim('getY', 0, lambda self: primitive_dictionary['getY']())
        
        primitive_dictionary['getOpX'] = self.getOpX
        palette.add_block('getOpX',
                     style='box-style',
                     label=_('x coor. Enemy'),
                     prim_name='getOpX',
                     help_string=_('get the x coordinate of the Enemy'))
        self.tw.lc.def_prim('getOpX', 0, lambda self: primitive_dictionary['getOpX']())
        
        primitive_dictionary['getOpY'] = self.getOpY
        palette.add_block('getOpY',
                     style='box-style',
                     label=_('y coor. Enemy'),
                     prim_name='getOpY',
                     help_string=_('get the y coordinate of the Enemy'))
        self.tw.lc.def_prim('getOpY', 0, lambda self: primitive_dictionary['getOpY']())
        
        primitive_dictionary['getRot'] = self.getRot
        palette.add_block('getRot',
                     style='box-style',
                     label=_('rotation SumBot'),
                     prim_name='getRot',
                     help_string=_('get the rotation of the Sumbot'))
        self.tw.lc.def_prim('getRot', 0, lambda self: primitive_dictionary['getRot']())
        
        primitive_dictionary['getOpRot'] = self.getOpRot
        palette.add_block('getOpRot',
                     style='box-style',
                     label=_('rotation Enemy'),
                     prim_name='getOpRot',
                     help_string=_('get the rotation of the Enemy'))
        self.tw.lc.def_prim('getOpRot', 0, lambda self: primitive_dictionary['getOpRot']())
        
        primitive_dictionary['getDistCenter'] = self.getDistCenter
        palette.add_block('getDistCenter',
                     style='box-style',
                     label=_('distance to center'),
                     prim_name='getDistCenter',
                     help_string=_('get the distance to the center of the dohyo'))
        self.tw.lc.def_prim('getDistCenter', 0, lambda self: primitive_dictionary['getDistCenter']())
        
        primitive_dictionary['getDistOp'] = self.getDistOp
        palette.add_block('getDistOp',
                     style='box-style',
                     label=_('distance to Enemy'),
                     prim_name='getDistOp',
                     help_string=_('get the distance to the Enemy'))
        self.tw.lc.def_prim('getDistOp', 0, lambda self: primitive_dictionary['getDistOp']())
        
        primitive_dictionary['updateState'] = self.updateState
        palette.add_block('updateState',
                     style='basic-style',
                     label=_('update information'),
                     prim_name='updateState',
                     help_string=_('update information from the server'))
        self.tw.lc.def_prim('updateState', 0, lambda self: primitive_dictionary['updateState']())

    ############################### Turtle signals ############################

    def start(self):
        pass

    def quit(self):
        self.api.liberarRecursos()

    def stop(self):
        pass

    ###########################################################################

    # Sumtia helper functions for apiSumoUY.py interaction

    def sendVelocities(self,vel_izq = 0, vel_der = 0):
        self.api.enviarVelocidades(vel_izq, vel_der)
        
    def setVel(self,vel = 0):
        self.vel = int(vel)

    def forwardSumtia(self):
        self.api.enviarVelocidades(self.vel, self.vel)

    def backward(self):
        self.api.enviarVelocidades(-self.vel, -self.vel)
        
    def stopSumtia(self):
        self.api.enviarVelocidades(0,0)

    def turnLeft(self):
        self.api.enviarVelocidades(-self.vel, self.vel)


    def turnRight(self):
        self.api.enviarVelocidades(self.vel, -self.vel)
        
    def getX(self):
        return self.api.getCoorX()
    
    def getY(self):
        return self.api.getCoorY()
    
    def getOpX(self):
        return self.api.getCoorXOp()
    
    def getOpY(self):
        return self.api.getCoorYOp()
    
    def getRot(self):
        return self.api.getRot()
    
    def getOpRot(self):
        return self.api.getRotOp()

    def angleToCenter(self):
        rot = math.degrees(math.atan2(self.api.getCoorY(), self.api.getCoorX())) + (180 - self.getRot())
        return (rot - 360) if abs(rot) > 180 else rot 

    def angleToOpponent(self):
        x = self.getX() - self.getOpX()
        y = self.getY() - self.getOpY()
        rot = math.degrees(math.atan2(y, x)) + (180 - self.getRot())
        return (rot - 360) if abs(rot) > 180 else rot 
    
    def getDistCenter(self):
        return math.sqrt(math.pow(self.getX(), 2) + math.pow(self.getY(), 2))
    
    def getDistOp(self):
        return math.sqrt(math.pow(self.getX() - self.getOpX(), 2) +
                        math.pow(self.getY() - self.getOpY(), 2))
    
    def updateState(self):
        err = self.api.getInformacion()
        if err == -1:
            print "Error getting information"


