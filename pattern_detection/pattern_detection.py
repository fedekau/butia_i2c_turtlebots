#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path
from plugins.plugin import Plugin
from TurtleArt.tapalette import make_palette
from TurtleArt.taconstants import CONSTANTS
from TurtleArt.taconstants import MEDIA_SHAPES, NO_IMPORT, SKIN_PATHS, EXPAND_SKIN, BLOCKS_WITH_SKIN
from TurtleArt.taprimitive import Primitive, ArgSlot, ConstantArg
from TurtleArt.tatype import TYPE_INT, TYPE_STRING, TYPE_BOOL
SKIN_PATHS.append('plugins/pattern_detection/images')

from gettext import gettext as _

from library import patternsAPI

class Pattern_detection(Plugin):

    def __init__(self, parent):
        Plugin.__init__(self)
        self.tw = parent
        self.isInit = False
        self._path = os.path.dirname(__file__)
        self.detection = patternsAPI.detection()

    def setup(self):

        palette = make_palette('pattern_detection', ["#00FF00","#008000"], _('Pattern detection'),
                                translation=_('pattern_detection'))

        palette.add_block('isPresent',
                    style='boolean-1arg-block-style',
                    label=_('Seeing signal'),
                    prim_name='isPresent',
                    help_string= _('Returns True if the signal is in front of the camera'))
        self.tw.lc.def_prim('isPresent', 1,
            Primitive(self.isPresent, TYPE_BOOL, arg_descs=[ArgSlot(TYPE_STRING)]))

        palette.add_block('getDist',
                    style='number-style-1arg',
                    label=_('Distance to signal'),
                    prim_name='getDist',
                    help_string= _('Returns the distance of the siganl to the camera in milimeters'))
        self.tw.lc.def_prim('getDist', 1,
            Primitive(self.getDist, TYPE_INT, [ArgSlot(TYPE_STRING)]))

        #TODO: Faltaria ver si levanta el objet_data segun el idioma
        #obtener identificadores del api y cargar botones con imagenes.
        out = self.detection.arMultiGetIdsMarker()

        for section_name in out.split(";"):
            self._add_signal_botton(palette, section_name, section_name)


    ############################### Turtle signals ############################

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

    def _add_signal_botton(self, palette, block, help):
        global CONSTANTS
        CONSTANTS[block] = block
        block_name = block + "Pat"
        iconPath = os.path.abspath(os.path.join(self._path, 'images', block_name + 'off.svg'))
        if os.path.exists(iconPath):
            palette.add_block(block_name,
                            style='box-style-media',
                            prim_name=block_name,
                            help_string= help)
            BLOCKS_WITH_SKIN.append(block_name)
            NO_IMPORT.append(block_name)
            MEDIA_SHAPES.append(block_name)
            MEDIA_SHAPES.append(block_name + 'off')
            MEDIA_SHAPES.append(block_name + 'small')
            EXPAND_SKIN[block_name] = (0, 10)
        else:
            palette.add_block(block_name,
                            style='box-style',
                            label=block,
                            help_string=help,
                            prim_name=block_name)
        self.tw.lc.def_prim(block_name, 0,
            Primitive(CONSTANTS.get, TYPE_STRING, [ConstantArg(block)]))

        
    def isPresent(self, valor):
        self._start_cam()
        return (self.detection.isMarkerPresent(valor) == 1)

    def getDist(self, valor):
        self._start_cam()
        return self.detection.getMarkerTrigDist(valor)


