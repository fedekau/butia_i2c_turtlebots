#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Andrés Aguirre Dorelo <aaguirre@fing.edu.uy>
# Rafael Carlos Cordano Ottati <rafael.cordano@gmail.com>
# Lucía Carozzi <lucia.carozzi@gmail.com>
# Maria Eugenia Curi <mauge8@gmail.com>
# Leonel Peña <lapo26@gmail.com>
#
# MINA/INCO/UDELAR
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import os
import sys

from gettext import gettext as _

from plugins.plugin import Plugin
from TurtleArt.tapalette import make_palette
from TurtleArt.taprimitive import Primitive, ArgSlot
from TurtleArt.tatype import TYPE_INT
from TurtleArt.tatype import TYPE_NUMBER
from TurtleArt.tatype import TYPE_COLOR
import logging
LOGGER = logging.getLogger('turtleart-activity x11 events plugin')
sys.path.append(os.path.abspath('./plugins/Xevents'))
import plugins.Xevents.lib_event as lib_event


class Xevents(Plugin):

    def __init__(self, parent):
        Plugin.__init__(self)
        self._parent = parent
        self.running_sugar = self._parent.running_sugar
        self._status = True
        self.pause = 0

    def setPause(self, arg):
        self.pause = arg

    def getPause(self):
        return self.pause

    def setup(self):
        # set up X11 events specific blocks
        palette = make_palette('xlib-bots',
                               colors=["#FF6060", "#A06060"],
                               help_string=_('Palette of X11 event blocks'))

        palette.add_block('setX11mouse',
                          style='basic-style-2arg',
                          label=_('setXY'),
                          value_block=True,
                          default=[0, 0],
                          help_string=_('set the mouse pointer to' +
                                        'x y coordinates'),
                          prim_name='set_x11_mouse')

        palette.add_block('getX11mouseX',
                          style='box-style',
                          label=_('getMouseX'),
                          value_block=True,
                          help_string=_('get the mouse pointer x coordinate'),
                          prim_name='get_x11_mouse_x')

        palette.add_block('getX11mouseY',
                          style='box-style',
                          label=_('getMouseY'),
                          value_block=True,
                          help_string=_('get the mouse pointer y coordinate'),
                          prim_name='get_x11_mouse_y')

        palette.add_block('leftClick',
                          style='box-style',
                          label=_('leftClick'),
                          value_block=True,
                          help_string=_('click left click'),
                          prim_name='left_click')

        palette.add_block('rightClick',
                          style='box-style',
                          label=_('rightClick'),
                          value_block=True,
                          help_string=_('click right click'),
                          prim_name='right_click')

        palette.add_block('true',
                          style='box-style',
                          label=_('true'),
                          value_block=True,
                          help_string=_('true'),
                          prim_name='true')

        palette.add_block('false',
                          style='box-style',
                          label=_('false'),
                          value_block=True,
                          help_string=_('false'),
                          prim_name='false')

        palette.add_block('click',
                          style='basic-style-1arg',
                          label=_('click'),
                          value_block=True,
                          default=[1],
                          help_string=_('simulate a mouse click'),
                          prim_name='click')

        palette.add_block('getScreenWidth',
                          style='box-style',
                          label=_('getScreenWidth'),
                          value_block=True,
                          help_string=_('get the screen width'),
                          prim_name='get_screen_width')

        palette.add_block('getScreenHeight',
                          style='box-style',
                          label=_('getScreenHeight'),
                          value_block=True,
                          help_string=_('get the screen height'),
                          prim_name='get_screen_height')

        palette.add_block('pressButton',
                          style='basic-style-1arg',
                          label=_('pressButton'),
                          value_block=True,
                          default=[0],
                          help_string=_('keeps button pressed'),
                          prim_name='press_button')

        palette.add_block('releaseButton',
                          style='basic-style-1arg',
                          label=_('releaseButton'),
                          value_block=True,
                          default=[0],
                          help_string=_('releases button'),
                          prim_name='release_button')

        palette.add_block('freeze',
                          style='basic-style-1arg',
                          label=_('freeze bar'),
                          value_block=True,
                          default=[0],
                          help_string=_('freeze the bar'),
                          prim_name='freeze')

        palette.add_block('setLineColorRGB',
                          style='basic-style-3arg',
                          label=_('setLineColorRGB'),
                          value_block=True,
                          default=[0, 0, 0],
                          help_string=_('set line color from rgb value'),
                          prim_name='set_line_color_rgb')

        palette.add_block('setLineColor',
                          style='basic-style-1arg',
                          label=_('setLineColor'),
                          value_block=True,
                          help_string=_('set line color'),
                          prim_name='set_line_color')

        palette.add_block('setLineOpacity',
                          style='basic-style-1arg',
                          label=_('setLineOpacity'),
                          value_block=True,
                          default=[1],
                          help_string=_('set line opacity'),
                          prim_name='set_line_opacity')

        palette.add_block('showLine',
                          style='basic-style-1arg',
                          label=_('showLine'),
                          value_block=True,
                          default=[1],
                          help_string=_('show vertical line ' +
                                        'over mouse'),
                          prim_name='show_line')

        palette.add_block('setLineWidth',
                          style='basic-style-1arg',
                          label=_('setLineWidth'),
                          value_block=True,
                          default=[0],
                          help_string=_('width of vertical' +
                                        ' line over mouse'),
                          prim_name='set_line_width')

        palette.add_block('setLineHeight',
                          style='basic-style-1arg',
                          label=_('setLineHeight'),
                          value_block=True,
                          default=[0],
                          help_string=_('height of vertical' +
                                        ' line over mouse'),
                          prim_name='set_line_height')

        palette.add_block('setLineWidthAndHeigth',
                          style='basic-style-2arg',
                          label=_('setLineWidthAndHeigth'),
                          value_block=True,
                          default=[0, 0],
                          help_string=_('set width and height' +
                                        'of line over mouse'),
                          prim_name='set_line_width_and_heigth')

        self._parent.lc.def_prim(
            'set_x11_mouse', 2,
            Primitive(self.set_x11_mouse, arg_descs=[ArgSlot(TYPE_NUMBER),
                                                     ArgSlot(TYPE_NUMBER)]))
        self._parent.lc.def_prim(
            'get_x11_mouse_x', 0,
            Primitive(self.get_x11_mouse_x, TYPE_INT))
        self._parent.lc.def_prim(
            'get_x11_mouse_y', 0,
            Primitive(self.get_x11_mouse_y, TYPE_INT))
        self._parent.lc.def_prim(
            'left_click', 0,
            Primitive(lambda x: 1, TYPE_INT))
        self._parent.lc.def_prim(
            'right_click', 0,
            Primitive(lambda x: 2, TYPE_INT))
        self._parent.lc.def_prim(
            'true', 0,
            Primitive(lambda x: 1, TYPE_INT))
        self._parent.lc.def_prim(
            'false', 0,
            Primitive(lambda x: 0, TYPE_INT))
        self._parent.lc.def_prim(
            'click', 1,
            Primitive(self.click, arg_descs=[ArgSlot(TYPE_NUMBER)]))
        self._parent.lc.def_prim(
            'get_screen_width', 0,
            Primitive(self.get_screen_width, TYPE_INT))
        self._parent.lc.def_prim(
            'get_screen_height', 0,
            Primitive(self.get_screen_height, TYPE_INT))
        self._parent.lc.def_prim(
            'press_button', 1,
            Primitive(self.press_button, arg_descs=[ArgSlot(TYPE_NUMBER)]))
        self._parent.lc.def_prim(
            'release_button', 1,
            Primitive(self.release_button, arg_descs=[ArgSlot(TYPE_NUMBER)]))
        self._parent.lc.def_prim(
            'set_line_color', 1,
            Primitive(self.set_line_color, arg_descs=[ArgSlot(TYPE_COLOR)]))
        self._parent.lc.def_prim(
            'freeze', 1,
            Primitive(self.setPause, arg_descs=[ArgSlot(TYPE_INT)]))
        self._parent.lc.def_prim(
            'set_line_color_rgb', 3,
            Primitive(self.set_line_color_rgb,
                      arg_descs=[ArgSlot(TYPE_INT),
                                 ArgSlot(TYPE_INT),
                                 ArgSlot(TYPE_INT)]))

        self._parent.lc.def_prim(
            'show_line', 1,
            Primitive(lambda tt, x: lib_event.show_line(x),
                      arg_descs=[ArgSlot(TYPE_NUMBER)]))
        self._parent.lc.def_prim(
            'set_line_width', 1,
            Primitive(self.set_line_width, arg_descs=[ArgSlot(TYPE_NUMBER)]))

        self._parent.lc.def_prim(
            'set_line_height', 1,
            Primitive(self.set_line_height, arg_descs=[ArgSlot(TYPE_NUMBER)]))

        self._parent.lc.def_prim(
            'set_line_width_and_heigth', 2,
            Primitive(self.set_line_width_and_heigth,
                      arg_descs=[ArgSlot(TYPE_NUMBER),
                                 ArgSlot(TYPE_NUMBER)]))

        self._parent.lc.def_prim(
            'set_line_opacity', 1,
            Primitive(lambda tt, x: lib_event.set_line_opacity(x),
                      arg_descs=[ArgSlot(TYPE_NUMBER)]))

    # Block primitives

    def set_x11_mouse(self, xcoord, ycoord):
        lib_event.create_absolute_mouse_event(int(xcoord), int(ycoord), self.getPause())

    @staticmethod
    def get_x11_mouse_x():
        xcoord = lib_event.get_mouse_position()[0]
        return xcoord

    @staticmethod
    def get_x11_mouse_y():
        ycoord = lib_event.get_mouse_position()[1]
        return ycoord

    @staticmethod
    def get_screen_width():
        xcoord = lib_event.get_screen_resolution()[0]
        return xcoord

    @staticmethod
    def get_screen_height():
        ycoord = lib_event.get_screen_resolution()[1]
        return ycoord

    @staticmethod
    def click(button):
        lib_event.click_button(button)

    @staticmethod
    def press_button(button):
        lib_event.press_button(button)

    @staticmethod
    def release_button(button):
        lib_event.release_button(button)

    @staticmethod
    def set_line_color(colorname):
        lib_event.set_line_color(colorname)

    @staticmethod
    def set_line_color_rgb(red, green, blue):
        lib_event.set_line_color_rgb(red, green, blue)

    @staticmethod
    def set_line_width(width):
        lib_event.set_line_width(width)

    @staticmethod
    def set_line_height(height):
        lib_event.set_line_height(height)

    @staticmethod
    def set_line_width_and_heigth(width, height):
        lib_event.set_line_width_and_heigth(width, height)
