#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os.path
import logging

from plugins.plugin import Plugin
from TurtleArt.tapalette import make_palette
from TurtleArt.talogo import primitive_dictionary
from TurtleArt.taconstants import MEDIA_SHAPES, NO_IMPORT, SKIN_PATHS, \
    EXPAND_SKIN, BLOCKS_WITH_SKIN

from gettext import gettext as _

plugin_name = 'pattern'
plugin_folder = 'pattern_detection'

sys.path.insert(0, os.path.abspath('./plugins/' + plugin_folder + '/library'))

import multiPatternDetectionAPI as detectionAPI

_logger = logging.getLogger('TurtleArt-activity pattern_detection plugin')

class Pattern_detection(Plugin):
    #Detection api class
    detection = None
    isInit = False

    def __init__(self, parent):
        self._parent = parent
        self.detection = detectionAPI.detection()

    def setup(self):

        SKIN_PATHS.append('plugins/' + plugin_folder + '/images')
        palette = make_palette(plugin_name,
                     colors=["#00FF00","#008000"],
                     help_string=_('Deteccion de marcas'))

        primitive_dictionary['isPresent'] = self._isPresent
        palette.add_block('isPresent',
                          style='boolean-1arg-block-style',
                          label=_('Viendo Señal'),
                          prim_name='isPresent',
                          help_string= _('Devuelve True si la señal esta en el campo visual de la camara'))
        self._parent.lc.def_prim('isPresent', 1,
                             lambda self, x: primitive_dictionary['isPresent'](x))

        primitive_dictionary['getMarkerTrigDist'] = self._getMarkerTrigDist
        palette.add_block('getMarkerTrigDist',
                          style='number-style-1arg',
                          label=_('Distancia Señal'),
                          prim_name='getMarkerTrigDist',
                          help_string= _('Devuelve la distancia a la camara en mm'))
        self._parent.lc.def_prim('getMarkerTrigDist', 1,
                             lambda self, x: primitive_dictionary['getMarkerTrigDist'](x))


        #TODO: Faltaria ver si levnta el objet_data segun el idioma
        #obtener identificadores del api y cargar botones con imagenes.
        out = self.detection.arMultiGetIdsMarker()

        for section_name in out.split(";"):
            self._add_signal_botton(palette, section_name, section_name)

    def stop(self):
        self._stop_cam()

    def quit(self):
        self._stop_cam()

    def clear(self):
        self._stop_cam()

    def start(self):
        pass

    def end(self):
        print "end pattern_detection"

    def _stop_cam(self):
        if self.isInit:
            self.detection.cleanup()
            self.isInit = False

    def _start_cam(self):
        if not(self.isInit):
            self.detection.init()
            self.isInit = True

    def _add_signal_botton(self, palette, block_name, label):

        #If icon exists, use it instead of just the label
        iconPath = os.path.abspath(os.path.join(os.path.dirname(__file__), 'images', block_name + 'off.svg'))

        if os.path.exists(iconPath):
            palette.add_block(block_name,
                            style='box-style-media',
                            label='',
                            default=block_name,
                            prim_name=block_name,
                            help_string= label)
            BLOCKS_WITH_SKIN.append(block_name)
            NO_IMPORT.append(block_name)
            MEDIA_SHAPES.append(block_name)
            MEDIA_SHAPES.append(block_name + 'off')
            MEDIA_SHAPES.append(block_name + 'small')
            EXPAND_SKIN[block_name] = (0, 10)
        else:
            palette.add_block(block_name,
                            style='box-style',
                            label=block_name,
                            default=block_name,
                            prim_name=block_name,
                            help_string= label)
        self._parent.lc.def_prim(block_name, 0, lambda self: block_name)

    def _isPresent(self, valor):
        self._start_cam()
        return (self.detection.isMarkerPresent(valor) == 1)

    def _getMarkerTrigDist(self, valor):
        self._start_cam()
        return self.detection.getMarkerTrigDist(valor)


