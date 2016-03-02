#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Andrés Aguirre Dorelo <aaguirre@fing.edu.uy>
# Rafael Carlos Cordano Ottati <rafael.cordano@gmail.com>
# Lucía Carozzi <lucia.carozzi@gmail.com>
# Maria Eugenia Curi <mauge8@gmail.com>
# Leonel Peña <lapo26@gmail.com>
# Andrés Vasilev <andresvasilev@gmail.com>
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
import time

sys.path.append(os.path.abspath('./plugins/xevents'))

from gettext import gettext as _
from collections import Counter

from plugins.plugin import Plugin
from TurtleArt.tapalette import make_palette
from TurtleArt.taprimitive import Primitive, ArgSlot, ConstantArg
from TurtleArt.tatype import TYPE_INT, TYPE_NUMBER, TYPE_COLOR, TYPE_STRING
from events import Events
from TurtleArt.taconstants import CONSTANTS, MACROS


import logging
LOGGER = logging.getLogger('turtleart-activity x11 events plugin')

class Xevents(Plugin):

    def __init__(self, parent):
        Plugin.__init__(self)
        self._parent = parent
        self.running_sugar = self._parent.running_sugar
        self._status = True
        self.pause = 0
        self._events = Events()
        self._buttons = {} #previous values from buttons {key:[value, lastDebounceTime]}


    def setPause(self):
        self.pause = True

    def unsetPause(self):
        self.pause = False    

    def getPause(self):
        return self.pause
        
    def stop(self):
      pass  

    def setup(self):
        # set up X11 events specific blocks
        global CONSTANTS
        CONSTANTS['left_click'] = 1
        CONSTANTS['right_click'] = 2
        CONSTANTS['TRUE'] = True
        CONSTANTS['FALSE'] = False

        CONSTANTS['xe_buffer_size'] = 10
        CONSTANTS['xe_spacebar'] = " "
        CONSTANTS['xe_left_arrow'] = "xe_left_arrow"
        CONSTANTS['xe_right_arrow'] = "xe_right_arrow"
        CONSTANTS['xe_up_arrow'] = "xe_up_arrow"
        CONSTANTS['xe_down_arrow'] = "xe_down_arrow"
        CONSTANTS['xe_tab'] = "\t"
        CONSTANTS['xe_return'] = "\r"
        CONSTANTS['xe_escape'] =  "\e"
        CONSTANTS['xe_enter'] =  "\n"

        global MACROS
        MACROS['setLineColorRGBmacro'] = [[0, 'setLineColorRGB', 0, 0, [None, 1, 2, 3, None]],
                                          [1, ['number', 0], 0, 0, [0, None]],
                                          [2, ['number', 0], 0, 0, [0, None]],
                                          [3, ['number', 0], 0, 0, [0, None]]
                                         ]

        MACROS['setLineWidthAndHeightmacro'] = [[0, 'setLineWidthAndHeight', 0, 0, [None, 1, 2, None]],
                                                [1, ['number', 0], 0, 0, [0, None]],
                                                [2, ['number', 0], 0, 0, [0, None]]
                                               ]


        palette = make_palette('xlib-bots',
                               colors=["#FF6060", "#A06060"],
                               help_string=_('Palette of X11 event blocks'))
        # Extra palette
        palette2 = make_palette('xlib-bots-extra', 
                                colors=["#FF6060", "#A06060"], 
                                help_string=_('Palette of X11 extra event blocks'))


        palette.add_block('setX11mouse',
                          style='basic-style-2arg',
                          label=_('setXY'),
                          value_block=True,
                          default=[0, 0],
                          help_string=_('set the mouse pointer to' +
                                        'x y coordinates'),
                          prim_name='set_x11_mouse')

        self._parent.lc.def_prim(
            'set_x11_mouse', 2,
            Primitive(self.set_x11_mouse, arg_descs=[ArgSlot(TYPE_NUMBER),
                                                     ArgSlot(TYPE_NUMBER)]))

        palette.add_block('getX11mouseX',
                          style='box-style',
                          label=_('getMouseX'),
                          value_block=True,
                          help_string=_('get the mouse pointer x coordinate'),
                          prim_name='get_x11_mouse_x')

        self._parent.lc.def_prim(
            'get_x11_mouse_x', 0,
            Primitive(self.get_x11_mouse_x, TYPE_INT))


        palette.add_block('getX11mouseY',
                          style='box-style',
                          label=_('getMouseY'),
                          value_block=True,
                          help_string=_('get the mouse pointer y coordinate'),
                          prim_name='get_x11_mouse_y')

        self._parent.lc.def_prim(
            'get_x11_mouse_y', 0,
            Primitive(self.get_x11_mouse_y, TYPE_INT))


        palette.add_block('getScreenWidth',
                          style='box-style',
                          label=_('getScreenWidth'),
                          value_block=True,
                          help_string=_('get the screen width'),
                          prim_name='get_screen_width')

        self._parent.lc.def_prim(
            'get_screen_width', 0,
            Primitive(self.get_screen_width, TYPE_INT))


        palette.add_block('getScreenHeight',
                          style='box-style',
                          label=_('getScreenHeight'),
                          value_block=True,
                          help_string=_('get the screen height'),
                          prim_name='get_screen_height')

        self._parent.lc.def_prim(
            'get_screen_height', 0,
            Primitive(self.get_screen_height, TYPE_INT))


        palette.add_block('click',
                          style='basic-style-1arg',
                          label=_('click'),
                          value_block=True,
                          default=[1],
                          help_string=_('simulate a mouse click'),
                          prim_name='click')

        self._parent.lc.def_prim(
            'click', 1,
            Primitive(self.click, arg_descs=[ArgSlot(TYPE_NUMBER)]))


        palette.add_block('doubleClick',
                          style='basic-style-1arg',
                          label=_('double click'),
                          value_block=True,
                          default=[1],
                          help_string=_('simulate a mouse double click'),
                          prim_name='double_click')

        self._parent.lc.def_prim(
            'double_click', 1,
            Primitive(self.double_click, arg_descs=[ArgSlot(TYPE_NUMBER)]))


        palette.add_block('pressButton',
                          style='basic-style-1arg',
                          label=_('pressButton'),
                          value_block=True,
                          default=[0],
                          help_string=_('keeps button pressed'),
                          prim_name='press_button')

        self._parent.lc.def_prim(
            'press_button', 1,
            Primitive(self.press_button, arg_descs=[ArgSlot(TYPE_NUMBER)]))


        palette.add_block('releaseButton',
                          style='basic-style-1arg',
                          label=_('releaseButton'),
                          value_block=True,
                          default=[0],
                          help_string=_('releases button'),
                          prim_name='release_button')

        self._parent.lc.def_prim(
            'release_button', 1,
            Primitive(self.release_button, arg_descs=[ArgSlot(TYPE_NUMBER)]))


        palette.add_block('leftClick',
                          style='box-style',
                          label=_('leftClick'),
                          value_block=True,
                          help_string=_('click left click'),
                          prim_name='left_click')

        self._parent.lc.def_prim(
            'left_click', 0,
            Primitive(CONSTANTS.get, TYPE_INT, [ConstantArg('left_click')]))


        palette.add_block('rightClick',
                          style='box-style',
                          label=_('rightClick'),
                          value_block=True,
                          help_string=_('click right click'),
                          prim_name='right_click')

        self._parent.lc.def_prim(
            'right_click', 0,
            Primitive(CONSTANTS.get, TYPE_INT, [ConstantArg('right_click')]))


        palette.add_block('freeze',
                          style='basic-style',
                          label=_('freezeBar'),
                          value_block=True,
                          help_string=_('freeze the bar'),
                          prim_name='freeze')

        self._parent.lc.def_prim(
            'freeze', 0,
            Primitive(self.setPause))


        '''

        palette.add_block('freeze',
                          style='basic-style-1arg',
                          label=_('freeze bar'),
                          value_block=True,
                          default=[0],
                          help_string=_('freeze the bar'),
                          prim_name='freeze')

        self._parent.lc.def_prim(
            'freeze', 1,
            Primitive(self.setPause, arg_descs=[ArgSlot(TYPE_INT)]))
        '''

        palette.add_block('unfreeze',
                          style='basic-style',
                          label=_('unfreezeBar'),
                          value_block=True,
                          help_string=_('unfreeze the bar'),
                          prim_name='unfreeze')

        self._parent.lc.def_prim(
            'unfreeze', 0,
            Primitive(self.unsetPause))


        palette.add_block('showLine',
                          style='basic-style',
                          label=_('showLine'),
                          value_block=True,
                          help_string=_('show vertical line over mouse'),
                          prim_name='show_line')

        self._parent.lc.def_prim(
            'show_line', 0,
            Primitive(self.show_line))


        palette.add_block('hideLine',
                          style='basic-style',
                          label=_('hideLine'),
                          value_block=True,
                          help_string=_('hide vertical line over mouse'),
                          prim_name='hide_line')

        self._parent.lc.def_prim(
            'hide_line', 0,
            Primitive(self.hide_line))


        palette.add_block('setLineColorRGB',
                          hidden=True,
                          style='basic-style-3arg',
                          label=_('setLineColorRGB'),
                          value_block=True,
                          default=[0, 0, 0],
                          help_string=_('set line color from rgb value'),
                          prim_name='set_line_color_rgb')

        self._parent.lc.def_prim(
            'set_line_color_rgb', 3,
            Primitive(self.set_line_color_rgb,
                      arg_descs=[ArgSlot(TYPE_INT),
                                 ArgSlot(TYPE_INT),
                                 ArgSlot(TYPE_INT)]))


        palette.add_block('setLineColorRGBmacro',
                          style='basic-style-extended-vertical',
                          label=_('setLineColorRGB'),
                          help_string=_('set line color from rgb value'))


        palette.add_block('setLineColor',
                          style='basic-style-1arg',
                          label=_('setLineColor'),
                          value_block=True,
                          help_string=_('set line color'),
                          prim_name='set_line_color')

        self._parent.lc.def_prim(
            'set_line_color', 1,
            Primitive(self.set_line_color, arg_descs=[ArgSlot(TYPE_COLOR)]))


        palette.add_block('setLineOpacity',
                          style='basic-style-1arg',
                          label=_('setLineOpacity'),
                          value_block=True,
                          default=[1],
                          help_string=_('set line opacity'),
                          prim_name='set_line_opacity')

        self._parent.lc.def_prim(
            'set_line_opacity', 1,
            Primitive(self.set_line_opacity, arg_descs=[ArgSlot(TYPE_NUMBER)]))


        palette.add_block('setLineWidthAndHeight',
                          hidden=True,
                          style='basic-style-2arg',
                          label=_('setLineWidthAndHeight'),
                          value_block=True,
                          default=[0, 0],
                          help_string=_('set width and height of line over mouse'),
                          prim_name='set_line_width_and_height')

        self._parent.lc.def_prim(
            'set_line_width_and_height', 2,
            Primitive(self.set_line_width_and_height,
                      arg_descs=[ArgSlot(TYPE_NUMBER),
                                 ArgSlot(TYPE_NUMBER)]))

        palette.add_block('setLineWidthAndHeightmacro',
                          style='basic-style-extended-vertical',
                          label=_('setLineWidthAndHeight'),
                          help_string=_('set width and height of line over mouse'))


        palette.add_block('setLineWidth',
                          style='basic-style-1arg',
                          label=_('setLineWidth'),
                          value_block=True,
                          default=[0],
                          help_string=_('width of vertical line over mouse'),
                          prim_name='set_line_width')

        self._parent.lc.def_prim(
            'set_line_width', 1,
            Primitive(self.set_line_width, arg_descs=[ArgSlot(TYPE_NUMBER)]))


        palette.add_block('setLineHeight',
                          style='basic-style-1arg',
                          label=_('setLineHeight'),
                          value_block=True,
                          default=[0],
                          help_string=_('height of vertical line over mouse'),
                          prim_name='set_line_height')

        self._parent.lc.def_prim(
            'set_line_height', 1,
            Primitive(self.set_line_height, arg_descs=[ArgSlot(TYPE_NUMBER)]))


        palette2.add_block('simulateKey',
                          style='basic-style-1arg',
                          label=_('simulateKey'),
                          help_string=_('simulates pressing a key'),
                          prim_name='simulate_key')

        self._parent.lc.def_prim(
            'simulate_key', 1,
            Primitive(self.simulate_key, arg_descs=[ArgSlot(TYPE_STRING)]))


        palette2.add_block('simulateCopy',
                          style='basic-style',
                          label=_('simulateCopy'),
                          help_string=_('simulate copy event'),
                          prim_name='copy_event')

        self._parent.lc.def_prim(
            'copy_event', 0,
            Primitive(self.copy_event))


        palette2.add_block('simulatePaste',
                          style='basic-style',
                          label=_('simulatePaste'),
                          help_string=_('simulate paste event'),
                          prim_name='paste_event')

        self._parent.lc.def_prim(
            'paste_event', 0,
            Primitive(self.paste_event))


        '''palette2.add_block('writeText',
                          style='basic-style-1arg',
                          label=_('writeText'),
		                      default=[_("Write your text")],
                          help_string=_('simulates writing a text'),
                          prim_name='write_text')

        self._parent.lc.def_prim(
            'write_text', 1,
            Primitive(self.write_text, arg_descs=[ArgSlot(TYPE_STRING)]))
        '''

        palette2.add_block('spaceBar',
                          style='box-style',
                          label=_('spaceBar'),
                          value_block=True,
                          help_string=_('space bar'),
                          prim_name='spacebar')

        self._parent.lc.def_prim(
            'spacebar', 0,
            Primitive(CONSTANTS.get, TYPE_STRING, [ConstantArg('xe_spacebar')]))


        palette2.add_block('leftArrow',
                          style='box-style',
                          label=_('leftArrow'),
                          value_block=True,
                          help_string=_('left arrow'),
                          prim_name='left_arrow')

        self._parent.lc.def_prim(
            'left_arrow', 0,
            Primitive(CONSTANTS.get, TYPE_STRING, [ConstantArg('xe_left_arrow')]))


        palette2.add_block('rightArrow',
                          style='box-style',
                          label=_('rightArrow'),
                          value_block=True,
                          help_string=_('right arrow'),
                          prim_name='right_arrow')

        self._parent.lc.def_prim(
            'right_arrow', 0,
            Primitive(CONSTANTS.get, TYPE_STRING, [ConstantArg('xe_right_arrow')]))


        palette2.add_block('upArrow',
                          style='box-style',
                          label=_('upArrow'),
                          value_block=True,
                          help_string=_('up arrow'),
                          prim_name='up_arrow')

        self._parent.lc.def_prim(
            'up_arrow', 0,
            Primitive(CONSTANTS.get, TYPE_STRING, [ConstantArg('xe_up_arrow')]))


        palette2.add_block('downArrow',
                          style='box-style',
                          label=_('downArrow'),
                          value_block=True,
                          help_string=_('down arrow'),
                          prim_name='down_arrow')

        self._parent.lc.def_prim(
            'down_arrow', 0,
            Primitive(CONSTANTS.get, TYPE_STRING, [ConstantArg('xe_down_arrow')]))


        palette2.add_block('tabKey',
                          style='box-style',
                          label=_('tabKey'),
                          value_block=True,
                          help_string=_('tab key'),
                          prim_name='tab_key')

        self._parent.lc.def_prim(
            'tab_key', 0,
            Primitive(CONSTANTS.get, TYPE_STRING, [ConstantArg('xe_tab')]))


        palette2.add_block('returnKey',
                          style='box-style',
                          label=_('returnKey'),
                          value_block=True,
                          help_string=_('return key'),
                          prim_name='return_key')

        self._parent.lc.def_prim(
            'return_key', 0,
            Primitive(CONSTANTS.get, TYPE_STRING, [ConstantArg('xe_return')]))


        palette2.add_block('escapeKey',
                          style='box-style',
                          label=_('escapeKey'),
                          value_block=True,
                          help_string=_('escape key'),
                          prim_name='escape_key')

        self._parent.lc.def_prim(
            'escape_key', 0,
            Primitive(CONSTANTS.get, TYPE_STRING, [ConstantArg('xe_escape')]))


        palette2.add_block('enterKey',
                          style='box-style',
                          label=_('enterKey'),
                          value_block=True,
                          help_string=_('enter key'),
                          prim_name='enter_key')

        self._parent.lc.def_prim(
            'enter_key', 0,
            Primitive(CONSTANTS.get, TYPE_STRING, [ConstantArg('xe_enter')]))


        '''
        palette2.add_block('simulateSpaceBar',
                  style='basic-style',
                  label=_('simulateSpaceBar'),
                  help_string=_('simulate spacebar event'),
                  prim_name='spacebar_event')

        self._parent.lc.def_prim(
            'spacebar_event', 0,
            Primitive(self.spacebar_event))


        palette2.add_block('simulateLeftArrow',
                  style='basic-style',
                  label=_('simulateLeftArrow'),
                  help_string=_('simulate left arrow event'),
                  prim_name='left_arrow_event')

        self._parent.lc.def_prim(
            'left_arrow_event', 0,
            Primitive(self.left_arrow_event))


        palette2.add_block('simulateRightArrow',
                  style='basic-style',
                  label=_('simulateRightArrow'),
                  help_string=_('simulate right arrow event'),
                  prim_name='right_arrow_event')

        self._parent.lc.def_prim(
            'right_arrow_event', 0,
            Primitive(self.right_arrow_event))


        palette2.add_block('simulateUpArrow',
                  style='basic-style',
                  label=_('simulateUpArrow'),
                  help_string=_('simulate up arrow event'),
                  prim_name='up_arrow_event')

        self._parent.lc.def_prim(
            'up_arrow_event', 0,
            Primitive(self.up_arrow_event))


        palette2.add_block('simulateDownArrow',
                  style='basic-style',
                  label=_('simulateDownArrow'),
                  help_string=_('simulate down arrow event'),
                  prim_name='down_arrow_event')

        self._parent.lc.def_prim(
            'down_arrow_event', 0,
            Primitive(self.down_arrow_event))

        '''

        palette2.add_block('scrollUp',
                  style='basic-style',
                  label=_('scrollUp'),
                  help_string=_('simulate mouse scroll up event'),
                  prim_name='scroll_up')

        self._parent.lc.def_prim(
            'scroll_up', 0,
            Primitive(self.scroll_up))


        palette2.add_block('scrollDown',
                  style='basic-style',
                  label=_('scrollDown'),
                  help_string=_('simulate mouse scroll down event'),
                  prim_name='scroll_down')

        self._parent.lc.def_prim(
            'scroll_down', 0,
            Primitive(self.scroll_down))


        palette2.add_block('debounce',
                        style='number-style-block',
                        label=[_('debounce'), _('unique_name'), _('button') ],
                        default=["unique name"],
                        help_string=_('debounce'),
                        prim_name='debounce')
        

        self._parent.lc.def_prim(
          'debounce', 2,
          Primitive(self.debounce, arg_descs=[ArgSlot(TYPE_STRING),
                                              ArgSlot(TYPE_NUMBER)]))

        palette2.add_block('webBrowser',
                          style='basic-style-1arg',
                          label=_('webBrowser'),
                          default=[_("http://www.example.com")],
                          help_string=_('simulates opening a web browser'),
                          prim_name='browser')

        self._parent.lc.def_prim(
            'browser', 1,
            Primitive(self.browser, arg_descs=[ArgSlot(TYPE_STRING)]))


    ############################# Turtle calls ################################

    def start(self):
        pass

    def stop(self):
        self._events.show_line(False)

    def quit(self):
        pass

    ################################# Primitives ##############################

    '''
      def write_text(self, text):
        self._events.write_text(text)
    '''

    def set_x11_mouse(self, x, y):
        self._events.create_absolute_mouse_event(int(x), int(y), self.getPause())

    def get_x11_mouse_x(self):
        return self._events.get_mouse_position()[0]

    def get_x11_mouse_y(self):
        return self._events.get_mouse_position()[1]

    def get_screen_width(self):
        return self._events.get_screen_resolution()[0]

    def get_screen_height(self):
        return self._events.get_screen_resolution()[1]

    def click(self, button):
        self._events.click_button(button)

    def double_click(self, button):
        self._events.double_click_button(button)

    def press_button(self, button):
        self._events.press_button(button)

    def release_button(self, button):
        self._events.release_button(button)

    def show_line(self):
        self._events.show_line(True)

    def hide_line(self):
        self._events.show_line(False)    

    def set_line_color(self, color_name):
        self._events.set_line_color(color_name)

    def set_line_opacity(self, opacity):
        self._events.set_line_opacity(opacity)

    def set_line_color_rgb(self, red, green, blue):
        self._events.set_line_color_rgb(red, green, blue)

    def set_line_width(self, width):
        self._events.set_line_width(width)

    def set_line_height(self, height):
        self._events.set_line_height(height)

    def set_line_width_and_height(self, width, height):
        self._events.set_line_width_and_height(width, height)

    def copy_event(self):
        self._events.copy_event()

    def paste_event(self):
        self._events.paste_event()

    '''
    def spacebar_event(self):
        self._events.spacebar_event()

    def left_arrow_event(self):
        self._events.left_arrow_event()

    def right_arrow_event(self):
        self._events.right_arrow_event()

    def up_arrow_event(self):
        self._events.up_arrow_event()

    def down_arrow_event(self):
        self._events.down_arrow_event()
    '''

    def scroll_up(self):
        self._events.scroll_up()

    def scroll_down(self):
        self._events.scroll_down()

    def simulate_key(self,key):
        self._events.simulate_key(key)

    def _listMode(self, l):

      data = Counter(l)
      if len(data) > 0:
        data.most_common() # Returns all unique items and their counts
        return data.most_common(1)[0][0] # Returns the highest occurring item
      else:
        return 0
          
    def debounce(self, buttonState, buttonName):
              
      #deboucing - recolectar lecturas en cierto tiempo y evaluar la cantidad de 0 y 1's
      #self.buttons -> key:[]
      if not self._buttons.has_key(buttonName):
        self._buttons[buttonName] = []
        
      self._buttons[buttonName].append(buttonState)
        
        
      if len(self._buttons[buttonName]) > CONSTANTS['xe_buffer_size']:
        self._buttons[buttonName].pop(0)
        
      if buttonState == 0 and self._listMode(self._buttons[buttonName]) == 1:
        #print buttonState
        #print buttonName
        #print self._buttons[buttonName]
        #print 1
          
        return 1
          
      else:
        #print 0
        return 0


    def browser(self, url):

      self._events.browser(url)