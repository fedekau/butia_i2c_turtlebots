
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
        msg = _('You will upgrade the USB4Butia firmware.\nNot disconnect the board and not close this activity.\nYou want to continue?')
        dialog = gtk.MessageDialog(self, 0, gtk.MESSAGE_WARNING, gtk.BUTTONS_OK_CANCEL, msg)
        dialog.set_title(_('Flashing USB4Butia board...'))
        res = dialog.run()
        dialog.destroy()

        if res == gtk.RESPONSE_OK:
            print 'A flashear!!'
            self.flash()

        elif res ==  gtk.RESPONSE_CANCEL:
            pass

    def flash(self):
        dialog = self.initing()
        proc = -1
        try:
            proc = subprocess.Popen(shlex.split("./fsusb --force_program usb4butia.hex"))
        except Exception, err:
            print 'Error in fsusb', err

        # How control the end of fusb flashing?
        time.sleep(4)

        dialog.destroy()

        if proc == -1:
            self.unsucess()
        else:
            self.sucess()

    def initing(self):
        msg = _('Flashing...')
        dialog = gtk.MessageDialog(self, 0, gtk.MESSAGE_INFO, gtk.BUTTONS_NONE, msg)
        dialog.set_title(_('Flashing USB4Butia board...'))
        # Run es bloqueante
        #dialog.run()
        dialog.show()
        return dialog

    def sucess(self):
        msg = _('The upgrade ends successfully!')
        dialog = gtk.MessageDialog(self, 0, gtk.MESSAGE_INFO, gtk.BUTTONS_CLOSE, msg)
        dialog.set_title(_('Flashing USB4Butia board...'))
        dialog.run()
        dialog.destroy()

    def unsucess(self):
        msg = _('The upgrade fails. Try again.')
        dialog = gtk.MessageDialog(self, 0, gtk.MESSAGE_INFO, gtk.BUTTONS_CLOSE, msg)
        dialog.set_title(_('Flashing USB4Butia board...'))
        dialog.run()
        dialog.destroy()
