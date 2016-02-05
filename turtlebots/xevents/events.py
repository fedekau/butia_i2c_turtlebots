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


from Xlib import X
from Xlib import display
from Xlib import ext
from Xlib.ext import xtest
#Do not remove the following imports as this gives some errores
from Xlib.ext import record
from Xlib.ext import shape
from Xlib.ext import xinerama
import gtk
import logging

from sendkey import SendKey

COLORS = {'red': "#E61B00",
          'orange': "#FF9201",
          'yellow': "#FFE900",
          'green': "#0FEF1E",
          'cyan': "#0EF5EE",
          'blue': "#0000FF",
          'purple': "#C61DCC",
          'white': "#FFFFFF",
          'black': "#000000"}

CONSTANTS = {'left_click': 1,
             'right_click': 2}

class Events:


    def __init__(self, debug=True):

        self._debug = debug

        if self._debug:
            logging.basicConfig(level=logging.DEBUG,format='%(asctime)s - %(levelname)s - %(message)s')

        self._display = display.Display()


        self._screen = self._display.screen()
        self._xwindow = self._screen.root
        self._window = gtk.Window(gtk.WINDOW_POPUP)
        self._window.set_keep_above(True)
        self._window.set_opacity(1)
        self._window.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#234fdb"))
        self._window.set_decorated(False)
        self._window.add_events(gtk.gdk.KEY_PRESS_MASK |
                                gtk.gdk.POINTER_MOTION_MASK |
                                gtk.gdk.BUTTON_PRESS_MASK |
                                gtk.gdk.SCROLL_MASK)


    def get_screen_resolution(self):
        """Returns the screen resolution """
        resolution = self._display.screen().root.get_geometry()
        return resolution.width, resolution.height


    def set_line_opacity(self, opacity):
        """Sets the line opacity """
        self._window.set_opacity(opacity)


    def set_line_width(self, width):

        self._window.set_size_request(int(width), self._window.get_screen().get_height())

        if self._debug:
            print width
            print self._window.get_size_request()


    def set_line_height(self, height):

        self._window.set_size_request(self._window.get_screen().get_width(), int(height))

        if self._debug:
            print "height:%s" % height
            print self._window.get_size_request()


    def set_line_width_and_height(self, width, height):

        self._window.resize(int(width), int(height))

        if self._debug:
            print "width:%s" % width
            print self._window.get_size_request()


    def show_line(self, active):

        if active:
            self._window.show()
        else:
            self._window.hide()


    def set_line_color(self, color_name):

        color = gtk.gdk.color_parse(COLORS[color_name.get_number_name()])
        self._window.modify_bg(gtk.STATE_NORMAL, color)

        if self._debug:
            print color_name.get_number_name()


    def set_line_color_rgb(self, red, green, blue):

        red_hex = "%s" % hex(int(red)).split("x")[1]
        green_hex = "%s" % hex(int(green)).split("x")[1]
        blue_hex = "%s" % hex(int(blue)).split("x")[1]
        c_hex = "#%s%s%s" % (red_hex, green_hex, blue_hex)
        color = gtk.gdk.color_parse(c_hex)
        self._window.modify_bg(gtk.STATE_NORMAL, color)


    def create_relative_mouse_event(self, dx, dy):

        # move pointer to set relative location
        self._display.warp_pointer(dx, dy)
        self._display.sync()


    def get_mouse_position(self):

        data = self._display.screen().root.query_pointer()._data
        return data['root_x'], data['root_y']



    def create_absolute_mouse_event(self, x, y, stopped):

        self._window.warp_pointer(x, y)

        if stopped != 1:
            gtk.gdk.flush()
            self._window.move(x, y)
            gtk.gdk.flush()
            self._window.set_keep_above(True)
        self._display.sync()


    def press_button(self, button):
        """Simulates pressing a button
        press button 1, for middle mouse button use 2, for opposite button use 3"""

        ext.xtest.fake_input(self._display, X.ButtonPress, button)
        self._display.sync()


    def release_button(self, button):
        """Simulates releasing a button"""

        ext.xtest.fake_input(self._display, X.ButtonRelease, button)
        self._display.sync()


    def _click(self, button):

        self.press_button(button)
        # to make click we need to release the same button
        self.release_button(button)

        self.press_button(button)
        self.release_button(button)


    def click_button(self, button):
        """Simulates clicking a button"""

        x, y = self.get_mouse_position()
        self._window.warp_pointer(x - 20, y)
        self._window.set_keep_above(False)
        self._window.set_keep_below(True)

        # press button 1, for middle mouse button use 2, for opposite button use 3
        gtk.gdk.flush()
        self._window.hide()
        gtk.gdk.flush()

        self._click(button)


    def double_click_button(self, button):
        """Simulates double clicking a button"""

        x, y = self.get_mouse_position()
        self._window.warp_pointer(x - 20, y)
        self._window.set_keep_above(False)
        self._window.set_keep_below(True)

        # press button 1, for middle mouse button use 2, for opposite button use 3
        gtk.gdk.flush()
        self._window.hide()
        gtk.gdk.flush()

        self._click(button)
        self._click(button)


    def copy_event(self):

        SendKey.send_special_key("Ctrl C")


    def paste_event(self):

        SendKey.send_special_key("Ctrl V")


    def write_text(self, text):

        if self._debug:
            logging.debug(text)

        splitted_text = list(text)

        for key in splitted_text:
            SendKey.send_key(key)