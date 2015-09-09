#!/usr/bin/env python

import os
import urllib
import time
import threading
import sys
sys.path.insert(0, os.path.abspath('./plugins/butia'))

from gettext import gettext as _
from plugins.plugin import Plugin
from TurtleArt.tapalette import make_palette
from TurtleArt.tapalette import palette_name_to_index
from TurtleArt.tapalette import palette_blocks
from TurtleArt.tapalette import special_block_colors
from TurtleArt.taprimitive import Primitive , ArgSlot, ConstantArg
from TurtleArt.tatype import TYPE_STRING, TYPE_FLOAT, TYPE_NUMBER
from TurtleArt.tautils import debug_output
from TurtleArt.tawindow import block_names
from pybot import pybot_client

#constants definitions
ERROR = -1 # default return value in case of error
MAX_SENSOR_PER_TYPE = 6
RELAY_PORT = {}
MODULOS_CONECTADOS = []

COLOR_RED = ["#FF0000","#808080"]
COLOR_PRESENT = ["#00FF00","#008000"]
COLOR_NOTPRESENT = ["#A0A0A0","#808080"] 

class Atyarandu(Plugin):

    def __init__(self, parent):
        self._parent = parent
        self._status = True
        self.robot = pybot_client.robot()
        self.loop = 0
        self.actualizable = True
        self.refresh()
        self.modulos_conectados = []

    def setup(self):
        palette = make_palette('atyarandu',
                    colors=COLOR_PRESENT,
                    help_string=_('Palette of Renewable Energy'))

        palette.add_block('engrefreshagh',
                style='basic-style',
                label=_('Refresh Energy'),
                value_block=True,
                help_string=\
                    _('updates the status of the pallet and the Energy blocks'),
                prim_name='engrefreshagh')
        self._parent.lc.def_prim('engrefreshagh', 0,
                Primitive(self.prim_refresh,
                            return_type=TYPE_STRING))

        palette.add_block('enggenagh',
                style='box-style',
                label=_('Energy Generated'),
                value_block=True,
                help_string=\
                    _('Estimated value of renewable energy ( MW ) to generate in the next hour in Uruguay'),
                prim_name='enggenagh')
        self._parent.lc.def_prim('enggenagh', 0,
                Primitive(self.prim_enggen,
                            return_type=TYPE_FLOAT))

        palette.add_block('engmaxagh',
                style='box-style',
                label=_('Max Energy'),
                value_block=True,
                help_string=\
                    _('Nominal value of renewable energy ( MW ) that can be generated in Uruguay'),
                prim_name='engmaxagh')
        self._parent.lc.def_prim('engmaxagh', 0,
                Primitive(self.prim_engmax,
                            return_type=TYPE_FLOAT))

        palette.add_block('engrecagh',
                style='box-style',
                label=_('Recommended Energy'),
                value_block=True,
                help_string=\
                    _('The preferred value of renewable energy ( MW ) for use'),
                prim_name='engrecagh')
        self._parent.lc.def_prim('engrecagh', 0,
                Primitive(self.prim_engrec,
                            return_type=TYPE_FLOAT))

        palette.add_block('engoncagh',
                style='box-style',
                label=_('On'),
                value_block='On',
                help_string=\
                    _('Power on'),
                colors = COLOR_PRESENT,
                prim_name='engonagh')
        self._parent.lc.def_prim('engonagh', 0,
                                    Primitive(self.prim_on,return_type=TYPE_STRING))
            
        palette.add_block('engoffcagh',
                style='box-style',
                label=_('Off'),
                value_block='Off',
                colors = COLOR_RED,
                help_string=\
                    _('Power off'),
                prim_name='engoffagh')
        self._parent.lc.def_prim('engoffagh', 0,
                                    Primitive(self.prim_off,return_type=TYPE_STRING))
        global RELAY_PORT
        for m in range(MAX_SENSOR_PER_TYPE):
            if m == 0:
                ocultar = False
            else:
                ocultar = True
                n = m
            x = str(m+1)
            nombloque = 'relay' + x + 'agh'
            RELAY_PORT[nombloque] = 0
            palette.add_block(nombloque,
                                style='basic-style-1arg',
                                label=_('Relay'),
                                prim_name=nombloque,
                                default = 'On',
                                hidden = ocultar,
                                colors = COLOR_PRESENT,
                                help_string=\
                                    _('power on/off the relay, on/off'))
            self._parent.lc.def_prim(nombloque, 1,
                                    Primitive(self.prim_control,
                                            return_type=TYPE_STRING,
                                            arg_descs=[ArgSlot(TYPE_STRING),ConstantArg(nombloque)]))
            special_block_colors[nombloque] = COLOR_NOTPRESENT

################################  Functions  ################################

    def prim_refresh(self):
        #Refresh
        self.check_for_device()

    def prim_enggen(self):
        #Returns the estimated value (MW) of renewable energy generation for the next hour in Uruguay
        try:
            archivo = urllib.urlopen('https://www.fing.edu.uy/cluster/eolica/pron_pot_parques/GUASU.txt')
            dato = float (archivo.read())
            dato = round(dato, 2)
            archivo.close()
        except:
            dato = ERROR
        return dato

    def prim_engmax(self):
        #Returns the nominal value (MW) of renewable energy that can be generated in Uruguay
        try:
            archivo = urllib.urlopen('https://www.fing.edu.uy/cluster/eolica/pron_pot_parques/GUASUnom.txt')
            dato = float (archivo.read())
            dato = round(dato, 2)
            archivo.close()
        except:
            dato = ERROR
        return dato

    def prim_engrec(self):
        #Returns the nominal value (MW) of renewable energy that can be generated in Uruguay
        try:
            archivo = urllib.urlopen('https://www.fing.edu.uy/cluster/eolica/pron_pot_parques/EOLO.txt')
            dato = float (archivo.read())
            archivo.close()
            dato = round(dato, 2)
        except:
            dato = ERROR
        return dato

    def prim_on(self):
        #Signal ON relay
        return 'ON'

    def prim_off(self):
        #Signal Off relay
        return 'OFF'

    def prim_control(self,valor,nom):
        #Turns RELAY on and off: 1 means on, 0 means off
        port = RELAY_PORT[nom]
        if valor.upper() == 'ON':
            on_off = 1
            msj = 'The relay ' + str(port) + ': ON'
        elif valor.upper() == 'OFF':
            on_off = 0
            msj = 'The relay ' + str(port) + ': OFF'
        else:
            return 'ERROR: No use ' + str(valor) + ', use ON or OFF'
        self.robot.setRelay(port, on_off)
        return msj

################################ Turtle calls ################################

    def quit(self):
        self.actualizable = False
        self.pollthread.cancel()

################################             ################################

    def check_for_device(self):
        # if there exists new RELAY connected or disconections to the butia IO board, 
        # then it change the color of the blocks corresponding
        global RELAY_PORT
        
        regenerar_paleta = False
        index = palette_name_to_index('atyarandu')
        if index is not None:
            cant_modulos_conectados = 0
            l = self.robot.getModulesList()
            modulos_nuevos = []
            self.modulos_conectados = []
            mods = []
            for e in l:
                t = self.robot._split_module(e)
                #t = ('5', 'relay', '0')
                #print t
                if t[1] == 'relay':
                    self.modulos_conectados.append(t[0])
                    modulos_nuevos.append(t[0])
                    mods.append(t[1] + ":" + t[0])
            #print mods
            #print 'mod conectados', self.modulos_conectados
            modulos_nuevos = self.modulos_conectados[:]
            #genera = self.prim_enggen()
            #valor = self.prim_engrec()
            genera = 68
            valor = 60
            cont_relay = 0
            for blk in self._parent.block_list.list:
                if blk.name.endswith('agh'):
                    #blk.name = 'relay2agh'
                    if blk.name == 'enggenagh':
                        if genera >= 0:
                            if valor >= 0:
                                if genera >= valor:
                                    special_block_colors[blk.name] = COLOR_PRESENT
                                else:
                                    special_block_colors[blk.name] = COLOR_RED
                            else:
                                special_block_colors[blk.name] = COLOR_NOTPRESENT
                        else:
                            special_block_colors[blk.name] = COLOR_NOTPRESENT
                    elif blk.name == 'engrecagh':
                        if valor >= 0:
                            special_block_colors[blk.name] = COLOR_PRESENT
                        else:
                            special_block_colors[blk.name] = COLOR_NOTPRESENT
                    elif blk.name == 'engmaxagh':
                        if valor >= 0:
                            special_block_colors[blk.name] = COLOR_PRESENT
                        else:
                            special_block_colors[blk.name] = COLOR_NOTPRESENT
                    
                    elif blk.name[:5] == 'relay':
                        #print blk.name
                        #print RELAY_PORT[blk.name]
                        #if RELAY_PORT[blk.name] == 0:
                        if len(modulos_nuevos)>0:
                            RELAY_PORT[blk.name] = modulos_nuevos[0]
                            tmp = modulos_nuevos[0]
                            modulos_nuevos.remove(tmp)

                        tmp = 'relay:' + str(RELAY_PORT[blk.name])
                        #print 'tmp', tmp
                        if tmp in mods:
                            cant_modulos_conectados += 1
                            if (blk.type == 'proto'):
                                blk.set_visibility(True)
                                regenerar_paleta = True
                            label = 'relay:' + str(RELAY_PORT[blk.name])
                            
                            special_block_colors[blk.name] = COLOR_PRESENT
                        else:
                            label = 'relay'
                            if(blk.type == 'proto'):
                                regenerar_paleta = True
                                if (RELAY_PORT[blk.name] <> 0) | (blk.name == 'relay0agh'):
                                    #if cant_modulos_conectados == 0:
                                        #if len(modulos_nuevos) == 0:
                                            #cant_modulos_conectados = -1
                                    
                                    if not blk.get_visibility():
                                        blk.set_visibility(True)
                                else:
                                    blk.set_visibility(False)
                            special_block_colors[blk.name] = COLOR_NOTPRESENT
                        blk.spr.set_label(label)
                        block_names[blk.name][0] = label
                    blk.refresh()
        if regenerar_paleta:
            self._parent.regenerate_palette(index)

    def refresh (self):
        debug_output('refresh')
        if self._parent.get_init_complete():
            debug_output('Refresh')
            if self.actualizable:
                self.check_for_device()
        self.pollthread = threading.Timer(3, self.refresh)
        self.pollthread.start()

