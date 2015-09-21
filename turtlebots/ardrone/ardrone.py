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
import ardroneAPI

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

COLOR_NOTPRESENT = ["#A0A0A0","#808080"] 
COLOR_PRESENT = ["#00FF00","#008000"]

class Ardrone(Plugin):
    
    def __init__(self, parent):
        Plugin.__init__(self)
        self.tw = parent
        power_manager_off(True)
        
        # Variables de ArDrone.
        self.apiArDrone = ardroneAPI.ardroneAPI()
        
    def setup(self):

        # Creo paleta ArDrone.
        paletteardrone = make_palette('ardrone', COLOR_NOTPRESENT, _('ArDrone'), init_on_start=True, translation=_('ardrone'))

        # Agrego bloque intercambia estado de emergencia.
        paletteardrone.add_block('emergenciaDrone',  # Nombre del bloque.
                    style='basic-style',  # Estilo del bloque.
                    label=_('emergencia Drone'),  # Texto en el bloque.
                    prim_name='emergenciaDrone',  # code reference (see below)
                    help_string=_('intercambia estado de emergencia del drone'))
        # A continuacion definimos para el bloque:
        # def_prim toma 3 argumentos: nombre de la primitiva, el numero de argumentos y
        # la funcion a llamar, en este caso a la funcion despegar.
        self.tw.lc.def_prim('emergenciaDrone', 0, Primitive(self.emergenciaDrone))
        special_block_colors['emergenciaDrone'] = COLOR_PRESENT[:]
        
        # Agrego bloque que calibra drone.
        paletteardrone.add_block('calibrarDrone',  # Nombre del bloque.
                    style='basic-style',  # Estilo del bloque.
                    label=_('calibrar Drone'),  # Texto en el bloque.
                    prim_name='calibrarDrone',  # code reference (see below)
                    help_string=_('calibra el drone, tiene que estar en tierra'))
        # A continuacion definimos para el bloque:
        # def_prim toma 3 argumentos: nombre de la primitiva, el numero de argumentos y
        # la funcion a llamar, en este caso a la funcion despegar.
        self.tw.lc.def_prim('calibrarDrone', 0, Primitive(self.calibrarDrone))
        special_block_colors['calibrarDrone'] = COLOR_PRESENT[:]
        
        # Agrego bloque despegar ArDrone.
        paletteardrone.add_block('despegarDrone',  # Nombre del bloque.
                    style='basic-style',  # Estilo del bloque.
                    label=_('despegar Drone'),  # Texto en el bloque.
                    prim_name='despegarDrone',  # code reference (see below)
                    help_string=_('despega el drone'))
        # A continuacion definimos para el bloque:
        # def_prim toma 3 argumentos: nombre de la primitiva, el numero de argumentos y
        # la funcion a llamar, en este caso a la funcion despegar.
        self.tw.lc.def_prim('despegarDrone', 0, Primitive(self.despegarDrone))
        special_block_colors['despegarDrone'] = COLOR_PRESENT[:]
        
        # Agrego bloque aterrizar ArDrone.
        paletteardrone.add_block('aterrizarDrone',  # Nombre del bloque.
                    style='basic-style',  # Estilo del bloque.
                    label=_('aterrizar Drone'),  # Texto en el bloque.
                    prim_name='aterrizarDrone',  # code reference (see below)
                    help_string=_('aterrizar el drone'))
        # A continuacion definimos para el bloque:
        # def_prim toma 3 argumentos: nombre de la primitiva, el numero de argumentos y
        # la funcion a llamar, en este caso a la funcion despegar.
        self.tw.lc.def_prim('aterrizarDrone', 0, Primitive(self.aterrizarDrone))
        special_block_colors['aterrizarDrone'] = COLOR_PRESENT[:]
        
        # Agrego bloque para que flote el ArDrone.
        paletteardrone.add_block('flotarDrone',  # Nombre del bloque.
                    style='basic-style',  # Estilo del bloque.
                    label=_('flota Drone'),  # Texto en el bloque.
                    prim_name='flotarDrone',  # code reference (see below)
                    help_string=_('flota el drone'))
        # A continuacion definimos para el bloque:
        # def_prim toma 3 argumentos: nombre de la primitiva, el numero de argumentos y
        # la funcion a llamar, en este caso a la funcion despegar.
        self.tw.lc.def_prim('flotarDrone', 0, Primitive(self.flotarDrone))
        special_block_colors['flotarDrone'] = COLOR_PRESENT[:]
                
        # Agrego bloque izquierda ArDrone.
        paletteardrone.add_block('izquierdaDrone',  # Nombre del bloque.
                    style='basic-style',  # Estilo del bloque.
                    label=_('izquierda Drone'),  # Texto en el bloque.
                    prim_name='izquierdaDrone',  # code reference (see below)
                    help_string=_('izquierda el drone'))
        # A continuacion definimos para el bloque:
        # def_prim toma 3 argumentos: nombre de la primitiva, el numero de argumentos y
        # la funcion a llamar, en este caso a la funcion despegar.
        self.tw.lc.def_prim('izquierdaDrone', 0, Primitive(self.izquierdaDrone))
        special_block_colors['izquierdaDrone'] = COLOR_PRESENT[:]
                
        # Agrego bloque derecha ArDrone.
        paletteardrone.add_block('derechaDrone',  # Nombre del bloque.
                    style='basic-style',  # Estilo del bloque.
                    label=_('derecha Drone'),  # Texto en el bloque.
                    prim_name='derechaDrone',  # code reference (see below)
                    help_string=_('derecha el drone'))
        # A continuacion definimos para el bloque:
        # def_prim toma 3 argumentos: nombre de la primitiva, el numero de argumentos y
        # la funcion a llamar, en este caso a la funcion despegar.
        self.tw.lc.def_prim('derechaDrone', 0, Primitive(self.derechaDrone))
        special_block_colors['derechaDrone'] = COLOR_PRESENT[:]
                
        # Agrego bloque arriba ArDrone.
        paletteardrone.add_block('arribaDrone',  # Nombre del bloque.
                    style='basic-style',  # Estilo del bloque.
                    label=_('arriba Drone'),  # Texto en el bloque.
                    prim_name='arribaDrone',  # code reference (see below)
                    help_string=_('arriba el drone'))
        # A continuacion definimos para el bloque:
        # def_prim toma 3 argumentos: nombre de la primitiva, el numero de argumentos y
        # la funcion a llamar, en este caso a la funcion despegar.
        self.tw.lc.def_prim('arribaDrone', 0, Primitive(self.arribaDrone))
        special_block_colors['arribaDrone'] = COLOR_PRESENT[:]
                
        # Agrego bloque abajo ArDrone.
        paletteardrone.add_block('abajoDrone',  # Nombre del bloque.
                    style='basic-style',  # Estilo del bloque.
                    label=_('abajo Drone'),  # Texto en el bloque.
                    prim_name='abajoDrone',  # code reference (see below)
                    help_string=_('abajo el drone'))
        # A continuacion definimos para el bloque:
        # def_prim toma 3 argumentos: nombre de la primitiva, el numero de argumentos y
        # la funcion a llamar, en este caso a la funcion despegar.
        self.tw.lc.def_prim('abajoDrone', 0, Primitive(self.abajoDrone))
        special_block_colors['abajoDrone'] = COLOR_PRESENT[:]
        
        # Agrego bloque adelante ArDrone.
        paletteardrone.add_block('adelanteDrone',  # Nombre del bloque.
                    style='basic-style',  # Estilo del bloque.
                    label=_('adelante Drone'),  # Texto en el bloque.
                    prim_name='adelanteDrone',  # code reference (see below)
                    help_string=_('adelante el drone'))
        # A continuacion definimos para el bloque:
        # def_prim toma 3 argumentos: nombre de la primitiva, el numero de argumentos y
        # la funcion a llamar, en este caso a la funcion despegar.
        self.tw.lc.def_prim('adelanteDrone', 0, Primitive(self.adelanteDrone))
        special_block_colors['adelanteDrone'] = COLOR_PRESENT[:]

        # Agrego bloque atras ArDrone.
        paletteardrone.add_block('atrasDrone',  # Nombre del bloque.
                    style='basic-style',  # Estilo del bloque.
                    label=_('atrás Drone'),  # Texto en el bloque.
                    prim_name='atrasDrone',  # code reference (see below)
                    help_string=_('atras el drone'))
        # A continuacion definimos para el bloque:
        # def_prim toma 3 argumentos: nombre de la primitiva, el numero de argumentos y
        # la funcion a llamar, en este caso a la funcion despegar.
        self.tw.lc.def_prim('atrasDrone', 0, Primitive(self.atrasDrone))
        special_block_colors['atrasDrone'] = COLOR_PRESENT[:]
        
        # Agrego bloque girar izquierda ArDrone.
        paletteardrone.add_block('girarIzquierdaDrone',  # Nombre del bloque.
                    style='basic-style',  # Estilo del bloque.
                    label=_('girarIzquierda Drone'),  # Texto en el bloque.
                    prim_name='girarIzquierdaDrone',  # code reference (see below)
                    help_string=_('gira a la izquierda el drone'))
        # A continuacion definimos para el bloque:
        # def_prim toma 3 argumentos: nombre de la primitiva, el numero de argumentos y
        # la funcion a llamar, en este caso a la funcion despegar.
        self.tw.lc.def_prim('girarIzquierdaDrone', 0, Primitive(self.girarIzquierdaDrone))
        special_block_colors['girarIzquierdaDrone'] = COLOR_PRESENT[:]
                        
        # Agrego bloque girar derecha ArDrone.
        paletteardrone.add_block('girarDerechaDrone',  # Nombre del bloque.
                    style='basic-style',  # Estilo del bloque.
                    label=_('girarDerecha Drone'),  # Texto en el bloque.
                    prim_name='girarDerechaDrone',  # code reference (see below)
                    help_string=_('gira a la derecha el drone'))
        # A continuacion definimos para el bloque:
        # def_prim toma 3 argumentos: nombre de la primitiva, el numero de argumentos y
        # la funcion a llamar, en este caso a la funcion despegar.
        self.tw.lc.def_prim('girarDerechaDrone', 0, Primitive(self.girarDerechaDrone))
        special_block_colors['girarDerechaDrone'] = COLOR_PRESENT[:]


        # Retorna porcentaje de bateria.
        paletteardrone.add_block('bateriaDrone', 
                    style='box-style',
                    label=('batería Drone'),
                    prim_name='bateriaDrone',
                    help_string=_('retorna porcentaje de bateria del drone'))
        self.tw.lc.def_prim('bateriaDrone', 0, Primitive(self.bateriaDrone))
        special_block_colors['bateriaDrone'] = COLOR_PRESENT[:]
        
        # Retorna angulo Theta.
        paletteardrone.add_block('anguloTheta', 
                    style='box-style',
                    label=('ángulo Theta'),
                    prim_name='anguloTheta',
                    help_string=_('angulo theta del drone'))
        self.tw.lc.def_prim('anguloTheta', 0, Primitive(self.anguloTheta))
        special_block_colors['anguloTheta'] = COLOR_PRESENT[:]
        
        # Retorna angulo Phi.
        paletteardrone.add_block('anguloPhi', 
                    style='box-style',
                    label=('ángulo Phi'),
                    prim_name='anguloPhi',
                    help_string=_('retorna angulo Phi del drone'))
        self.tw.lc.def_prim('anguloPhi', 0, Primitive(self.anguloPhi))
        special_block_colors['anguloPhi'] = COLOR_PRESENT[:]
        
        # Retorna angulo Psi.
        paletteardrone.add_block('anguloPsi', 
                    style='box-style',
                    label=('ángulo Psi'),
                    prim_name='anguloPsi',
                    help_string=_('retorna angulo Psi del drone'))
        self.tw.lc.def_prim('anguloPsi', 0, Primitive(self.anguloPsi))
        special_block_colors['anguloPsi'] = COLOR_PRESENT[:]
        
        # Retorna altura.
        paletteardrone.add_block('alturaDrone', 
                    style='box-style',
                    label=('altura Drone'),
                    prim_name='alturaDrone',
                    help_string=_('altura del drone'))
        self.tw.lc.def_prim('alturaDrone', 0, Primitive(self.alturaDrone))
        special_block_colors['alturaDrone'] = COLOR_PRESENT[:]
        

    ################################ ArDrone calls ################################
    
    # Intercambia el estado de emergencia del drone.
    def emergenciaDrone(self):
        self.apiArDrone.emergencia()
        
    # Calibra el drone.
    def calibrarDrone(self):
        self.apiArDrone.calibrar()
        
    # El drone despega.
    def despegarDrone(self):
        self.apiArDrone.despegar()
        
    # El drone aterriza.
    def aterrizarDrone(self):
        self.apiArDrone.aterrizar()

    # El drone flota.
    def flotarDrone(self):
        self.apiArDrone.flotar()

    # El drone se mueve a la izquierda.
    def izquierdaDrone(self):
        self.apiArDrone.izquierda()
    
     # El drone se mueve a la derecha.
    def derechaDrone(self):
        self.apiArDrone.derecha()
        
    # El drone se mueve hacia arriba.
    def arribaDrone(self):
        self.apiArDrone.arriba()       
        
    # El drone se mueve hacia abajo.
    def abajoDrone(self):
        self.apiArDrone.abajo()  
    
    # El drone se mueve adelante.
    def adelanteDrone(self):
        self.apiArDrone.adelante()  
        
    # El drone se mueve hacia atras.
    def atrasDrone(self):
        self.apiArDrone.atras()  
        
    # El drone gira a la izquierda.
    def girarIzquierdaDrone(self):
        self.apiArDrone.girarIzquierda()  
        
    # El drone gira a la derecha.
    def girarDerechaDrone(self):
        self.apiArDrone.girarDerecha()  
        
        
    # Bateria del drone.
    def bateriaDrone(self):
        return self.apiArDrone.bateria()
    
    # Angulo Theta.
    def anguloTheta(self):
        return self.apiArDrone.anguloTheta()
    
    # Angulo Phi.
    def anguloPhi(self):
        return self.apiArDrone.anguloPhi()
    
    # Angulo Psi.
    def anguloPsi(self):
        return self.apiArDrone.anguloPsi()
    
    # Altura drone.
    def alturaDrone(self):
        return self.apiArDrone.altura()
    
        
    ################################ Turtle calls ################################

    # Cuando inicia el programa.
    def start(self):
        print "hola start"

    # Cuando detiene el programa.
    def stop(self, butia=False):
        # Por defecto hago que flote.
        self.flotarDrone()
        
    # Cuando quita el programa.
    def quit(self):
        # Desconecta drone.
        self.apiArDrone.apagar()

