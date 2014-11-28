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
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

from plugins.Xevents.Xlib import X
from plugins.Xevents.Xlib import display
from plugins.Xevents.Xlib import ext
from plugins.Xevents.Xlib.ext import record
from plugins.Xevents.Xlib.ext import xtest
from plugins.Xevents.Xlib.ext import shape
from plugins.Xevents.Xlib.ext import xinerama
import gtk

DISPLAY = display.Display()
SCREEN = DISPLAY.screen()
XWINDOW = SCREEN.root
XB, YB = False, False
WINDOW = gtk.Window(gtk.WINDOW_POPUP)
WINDOW.set_keep_above(True)
WINDOW.set_opacity(1)
COLOR = gtk.gdk.color_parse("#234fdb")
WINDOW.modify_bg(gtk.STATE_NORMAL, COLOR)
WINDOW.set_decorated(False)
WINDOW.add_events(gtk.gdk.KEY_PRESS_MASK |
                  gtk.gdk.POINTER_MOTION_MASK |
                  gtk.gdk.BUTTON_PRESS_MASK |
                  gtk.gdk.SCROLL_MASK)


def get_screen_resolution():
    ddisplay = display.Display()
    resolution = ddisplay.screen().root.get_geometry()
    return resolution.width, resolution.height


def set_line_opacity(opacity):
    WINDOW.set_opacity(opacity)


def set_line_width(width):
    # w, h = wwin.get_size()
    print width
    WINDOW.set_size_request(int(width), WINDOW.get_screen().get_height())
    print WINDOW.get_size_request()


def set_line_height(height):
    # w, h = wwin.get_size()
    print "height:%s" % height
    WINDOW.set_size_request(WINDOW.get_screen().get_width(), int(height))
    print WINDOW.get_size_request()


def set_line_width_and_heigth(width, height):
    WINDOW.resize(int(width), int(height))
    print WINDOW.get_size_request()


def show_line(active):
    if active:
        WINDOW.show()
    else:
        WINDOW.hide()

# Trying to use color blocks


def set_line_color(color_name):
    print color_name.get_number_name()
    colors_names = {"red": "#E61B00",
                    "orange": "#FF9201",
                    "yellow": "#FFE900",
                    "green": "#0FEF1E",
                    "cyan": "#0EF5EE",
                    "blue": "#0000FF",
                    "purple": "#C61DCC",
                    "white": "#FFFFFF",
                    "black": "#000000"}

    ccolor = gtk.gdk.color_parse(colors_names[color_name.get_number_name()])
    WINDOW.modify_bg(gtk.STATE_NORMAL, ccolor)
####


def set_line_color_rgb(red, green, blue):
    print red
    print green
    print blue
    red_hex = "%s" % hex(int(red)).split("x")[1]
    green_hex = "%s" % hex(int(green)).split("x")[1]
    blue_hex = "%s" % hex(int(blue)).split("x")[1]
    chex = "#%s%s%s" % (red_hex, green_hex, blue_hex)
    ccolor = gtk.gdk.color_parse(chex)
    WINDOW.modify_bg(gtk.STATE_NORMAL, ccolor)


def create_relative_mouse_event(deltax, deltay):
    ddisplay = display.Display()
    # move pointer to set relative location
    ddisplay.warp_pointer(deltax, deltay)
    ddisplay.sync()


def get_mouse_position():
    ddisplay = display.Display()
    data = ddisplay.screen().root.query_pointer()._data
    return data['root_x'], data['root_y']


def create_absolute_mouse_event(xcoord, ycoord, stopped):
    XWINDOW.warp_pointer(xcoord, ycoord)
    if stopped != 1:
        WINDOW.move(xcoord, ycoord)
        WINDOW.set_keep_above(True)
    DISPLAY.sync()


def button_press(button):
    ddisplay = display.Display()
    ext.xtest.fake_input(ddisplay, X.ButtonPress, button)
    ddisplay.sync()


def button_release(button):
    ddisplay = display.Display()
    ext.xtest.fake_input(ddisplay, X.ButtonRelease, button)
    ddisplay.sync()


def click_button(button):
    xcoord, ycoord = get_mouse_position()
    XWINDOW.warp_pointer(xcoord - 20, ycoord)
    #XWINDOW.warp_pointer(xcoord, ycoord)
    WINDOW.set_keep_above(False)
    WINDOW.set_keep_below(True)

    ddisplay = display.Display()
    # press button 1, for middle mouse button use 2, for opposite button use 3
    try:
        WINDOW.destroy()
        print "destroyed"
    except:
        print "not destroyed"
    ext.xtest.fake_input(ddisplay, X.ButtonPress, button)
    ddisplay.sync()
    # to make click we need to release the same button
    ext.xtest.fake_input(ddisplay, X.ButtonRelease, button)
    ddisplay.sync()

    ext.xtest.fake_input(ddisplay, X.ButtonPress, button)
    ddisplay.sync()

    ext.xtest.fake_input(ddisplay, X.ButtonRelease, button)
    ddisplay.sync()


def press_button(button):
    ddisplay = display.Display()
    # press button 1, for middle mouse button use 2, for opposite button use 3
    ext.xtest.fake_input(ddisplay, X.ButtonPress, button)
    ddisplay.sync()


def release_button(button):
    ddisplay = display.Display()
    # to make click we need to release the same button
    ext.xtest.fake_input(ddisplay, X.ButtonRelease, button)
    ddisplay.sync()

