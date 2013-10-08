#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path

from plugins.plugin import Plugin
from TurtleArt.tapalette import make_palette
from TurtleArt.talogo import primitive_dictionary
from TurtleArt.tautils import debug_output
from TurtleArt.taconstants import MEDIA_SHAPES, NO_IMPORT, SKIN_PATHS, \
    EXPAND_SKIN, BLOCKS_WITH_SKIN
SKIN_PATHS.append('plugins/pattern_detection/images')

from gettext import gettext as _

from library import patternsAPI

class Pattern_detection(Plugin):

    def __init__(self, parent):
        self.tw = parent
        self.detection = None
        self.isInit = False
        self.detection = patternsAPI.detection()

    def setup(self):

        debug_output('creating %s palette' % _('pattern_detection'), self.tw.running_sugar)
        palette = make_palette('pattern_detection', ["#00FF00","#008000"], _('Pattern detection'))

        primitive_dictionary['isPresent'] = self._isPresent
        palette.add_block('isPresent',
                          style='boolean-1arg-block-style',
                          label=_('Seeing signal'),
                          prim_name='isPresent',
                          help_string= _('Returns True if the signal is in front of the camera'))
        self.tw.lc.def_prim('isPresent', 1,
                             lambda self, x: primitive_dictionary['isPresent'](x))

        primitive_dictionary['getMarkerTrigDist'] = self._getMarkerTrigDist
        palette.add_block('getMarkerTrigDist',
                          style='number-style-1arg',
                          label=_('Distance to signal'),
                          prim_name='getMarkerTrigDist',
                          help_string= _('Returns the distance of the siganl to the camera in milimeters'))
        self.tw.lc.def_prim('getMarkerTrigDist', 1,
                             lambda self, x: primitive_dictionary['getMarkerTrigDist'](x))


        #TODO: Faltaria ver si levnta el objet_data segun el idioma
        #obtener identificadores del api y cargar botones con imagenes.
        out = self.detection.arMultiGetIdsMarker()

        for section_name in out.split(";"):
            self._add_signal_botton(palette, section_name, section_name)


    ############################### Turtle signals ############################

    def start(self):
        pass

    def quit(self):
        self._stop_cam()

    def stop(self):
        self._stop_cam()

    def clear(self):
        self._stop_cam()

    ###########################################################################

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
        self.tw.lc.def_prim(block_name, 0, lambda self: block_name)

    def _isPresent(self, valor):
        self._start_cam()
        return (self.detection.isMarkerPresent(valor) == 1)

    def _getMarkerTrigDist(self, valor):
        self._start_cam()
        return self.detection.getMarkerTrigDist(valor)


