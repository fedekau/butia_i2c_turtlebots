
import logging

import shlex
import subprocess
import sys, os
import time
import gtk
from gettext import gettext as _

from sugar.activity import activity
from sugar.graphics.toolbarbox import ToolbarBox
from sugar.graphics.toolbutton import ToolButton
from sugar.activity.widgets import ActivityToolbarButton
from sugar.activity.widgets import StopButton
from sugar.graphics.toolbarbox import ToolbarButton

class FlashingUSB4all:
    def __init__(self):
        pass

    def flash(self):
        dialog = create_flashing_init()
        proc = subprocess.Popen(shlex.split("./fsusb --force_program usb4butia.hex"))

def on_click(event):
    board = FlashingUSB4all()
    board.flash()


def create_flashing_init():
    return None


class ButiaFirmware(activity.Activity):

    def __init__(self, handle):
        activity.Activity.__init__(self, handle)

        print "activity running"

        self.build_toolbar()
 
        self.build_canvas()

    def build_toolbar(self):
        # Creates the Toolbox. It contains the Activity Toolbar, which is the
        # bar that appears on every Sugar window and contains essential
        # functionalities, such as the 'Collaborate' and 'Close' buttons.

        toolbox = ToolbarBox()

        activity_button = ActivityToolbarButton(self)
        toolbox.toolbar.insert(activity_button, -1)
        activity_button.show()

        # Blank space (separator) and Stop button at the end:
        separator = gtk.SeparatorToolItem()
        separator.props.draw = False
        separator.set_expand(True)
        toolbox.toolbar.insert(separator, -1)
        separator.show()

        stop_button = StopButton(self)
        toolbox.toolbar.insert(stop_button, -1)
        stop_button.show()

        self.set_toolbox(toolbox)
        toolbox.show()

        self.show_all()
        
    def build_canvas(self):
        #The canvas is the main section of every Sugar Window.
        # It fills all the area below the toolbox.

        box = gtk.VBox()
        img = gtk.Image()
        img.set_from_file("alert.svg")
        img.show()
        box.add(img) 

        box12 = gtk.HBox()
        button_accept = gtk.Button("CONTINUAR")
        button_accept.connect("clicked", self.warning_message)
        button_accept.show()
        box12.add(button_accept)
        box12.show()
        box.add(box12)
        box.show()

        self.set_canvas(box)

    def warning_message(self, widget):
        msg = _('This action will flash the USB4Butia board. Are you sure?')
        dialog = gtk.MessageDialog(None, 0, gtk.MESSAGE_WARNING, gtk.BUTTONS_OK_CANCEL, msg)
        dialog.set_title(_('Flashing USB4Butia board...'))
        res = dialog.run()
        dialog.destroy()

        if res == gtk.RESPONSE_OK:
            print 'A flashear!!'

        elif res ==  gtk.RESPONSE_CANCEL:
            pass

