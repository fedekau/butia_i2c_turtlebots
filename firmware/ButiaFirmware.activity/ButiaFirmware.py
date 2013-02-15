#! /usr/bin/env python
# -*- coding: utf-8 -*-

import logging

import shlex
import subprocess
import sys, os
import platform
import time
import gtk
from gettext import gettext as _

from sugar.activity import activity
from sugar.graphics.toolbarbox import ToolbarBox
from sugar.graphics.toolbutton import ToolButton
from sugar.activity.widgets import ActivityToolbarButton
from sugar.activity.widgets import StopButton
from sugar.graphics.toolbarbox import ToolbarButton

from pybot import usb4butia

class ButiaFirmware(activity.Activity):

    def __init__(self, handle):
        activity.Activity.__init__(self, handle)

        self.build_toolbar()
        flash = Flash(self)
        self.set_canvas(flash.build_canvas())
        self.show_all()
 

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


class Flash():

    def __init__(self, parent = None):
        self.parent = parent
        
    def build_canvas(self):
        #The canvas is the main section of every Sugar Window.
        # It fills all the area below the toolbox.

        box = gtk.VBox()
        img = gtk.Image()
        img.set_from_file("activity/fua-icon.svg")
        img.show()
        box.add(img)

        boxH = gtk.HBox()

        button_check = gtk.Button(_("Check version"))
        button_check.connect("clicked", self.check_message)
        button_check.show()
        boxH.add(button_check)

        button_accept = gtk.Button(_("CONTINUE"))
        button_accept.connect("clicked", self.warning_message)
        button_accept.show()
        boxH.add(button_accept)

        boxH.show()
        box.add(boxH)
        box.show()
        return box


    def warning_message(self, widget=None):
        msg = _('You will upgrade the USB4Butia firmware.\nNot disconnect the board and not close this activity.\nYou want to continue?')
        dialog = gtk.MessageDialog(self.parent, 0, gtk.MESSAGE_WARNING, gtk.BUTTONS_OK_CANCEL, msg)
        dialog.set_title(_('Flashing USB4Butia board...'))
        res = dialog.run()
        dialog.destroy()

        if res == gtk.RESPONSE_OK:
            self.flash()

        elif res ==  gtk.RESPONSE_CANCEL:
            pass

    def check_message(self, widget=None):
        msg = _('The current Firmware is %s') % self.get_version()
        dialog = gtk.MessageDialog(self.parent, 0, gtk.MESSAGE_INFO, gtk.BUTTONS_OK, msg)
        dialog.set_title(_('USB4Butia firmware version...'))
        res = dialog.run()
        dialog.destroy()

    def flash(self, show_dialogs=True):
        path = './fsusb/x32/fsusb'
        try:
            arq,so = platform.architecture()
            if arq == '32bit':
                path = './fsusb/x32/fsusb'
                print 'Use 32bits fsusb'
            else:
                path = './fsusb/x64/fsusb'
                print 'Use 64bits fsusb'
        except:
            print 'Error getting platform info'

        if show_dialogs:
            dialog = self.initing()

        proc = None
        try:
            proc = subprocess.Popen([path, '--force_program', 'USB4all-5.hex'])
        except Exception, err:
            print 'Error in fsusb:', err
            print 'Trying --program option'
            try:
                proc = subprocess.Popen([path, '--program', 'USB4all-5.hex'])
            except Exception, err:
                print 'Error in fsusb:', err

        i = time.time()
        if proc:
            proc.wait()
            f = time.time()
            t = f - i

        if show_dialogs:
            dialog.destroy()

        if proc and (proc.returncode == 0):
            if show_dialogs:
                self.sucess(int(t))
            else:
                msg = _('The upgrade ends successfully!\nThe process takes %s seconds') % t
                print msg
        else:
            if show_dialogs:
                self.unsucess(proc.returncode)
            else:
                msg = _('The upgrade fails. Try again.\nError: %s') % proc.returncode
                print msg

    def initing(self):
        msg = _('Flashing USB4Butia board...')
        dialog = gtk.MessageDialog(self.parent, 0, gtk.MESSAGE_INFO, gtk.BUTTONS_NONE, msg)
        dialog.set_title(_('Flashing...'))
        # Run es bloqueante
        #dialog.run()
        dialog.show()
        return dialog

    def sucess(self, seconds):
        msg = _('The upgrade ends successfully!\nThe process takes %s seconds') % seconds
        dialog = gtk.MessageDialog(self.parent, 0, gtk.MESSAGE_INFO, gtk.BUTTONS_CLOSE, msg)
        dialog.set_title(_('Flashing USB4Butia board...'))
        dialog.run()
        dialog.destroy()

    def unsucess(self, err):
        msg = _('The upgrade fails. Try again.\nError: %s') % err
        dialog = gtk.MessageDialog(self.parent, 0, gtk.MESSAGE_INFO, gtk.BUTTONS_CLOSE, msg)
        dialog.set_title(_('Flashing USB4Butia board...'))
        dialog.run()
        dialog.destroy()

    def get_version(self):
        b = usb4butia.USB4Butia()
        version = b.getFirmwareVersion()
        b.close()
        return version


if __name__ == "__main__":
    f = Flash()
    argv = sys.argv[:]
    if len(argv) > 1:
        argv = argv[1:]
        if argv[0] == 'silent':
            f.flash(False)
    else:
        f.warning_message()

