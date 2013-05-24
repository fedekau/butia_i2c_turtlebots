#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import gtk
import platform
import subprocess
import time
import ConfigParser
import gettext
from gettext import gettext as _

try:
    from sugar.activity import activity
    from sugar.graphics.toolbarbox import ToolbarBox
    from sugar.activity.widgets import ActivityToolbarButton
    from sugar.activity.widgets import StopButton
except Exception, err:
    print 'No sugar', err

import pybot
from pybot import usb4butia


class ButiaFirmware(activity.Activity):

    def __init__(self, handle):
        activity.Activity.__init__(self, handle)
        self.build_toolbar()
        flash = Flash(self)
        self.set_canvas(flash.build_canvas())
        self.show_all()

    def build_toolbar(self):
        toolbox = ToolbarBox()
        activity_button = ActivityToolbarButton(self)
        toolbox.toolbar.insert(activity_button, -1)
        activity_button.show()
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

    def __init__(self, parent=None):
        self.parent = parent
        self._version = 7
        self.firmware_hex = 'USB4Butia-7.hex'

    def get_translations(self):
        file_activity_info = ConfigParser.ConfigParser()
        activity_info_path = os.path.abspath('activity/activity.info')
        file_activity_info.read(activity_info_path)
        bundle_id = file_activity_info.get('Activity', 'bundle_id')
        self.activity_name = file_activity_info.get('Activity', 'name')
        path = os.path.abspath('locale')
        gettext.bindtextdomain(bundle_id, path)
        gettext.textdomain(bundle_id)
        global _
        _ = gettext.gettext

    def build_window(self):
        self.get_translations()
        win = gtk.Window()
        win.set_title(_('Butia Firmware Upgrader'))
        win.connect('delete_event', self._quit)
        canvas = self.build_canvas()
        win.add(canvas)
        win.show()
        gtk.main()

    def _quit(self, win, e):
        gtk.main_quit()
        exit()
        
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

        button_accept = gtk.Button(_("Burn Firmware"))
        button_accept.connect("clicked", self.warning_message)
        button_accept.show()
        boxH.add(button_accept)

        boxH.show()
        box.add(boxH)
        box.show()
        return box


    def warning_message(self, widget=None):
        msg = _('You will upgrade to the USB4Butia v%s firmware.\n') % self._version
        msg = msg + _('Not disconnect the board and not close this activity.\n')
        msg = msg + _('You want to continue?')
        dialog = gtk.MessageDialog(self.parent, 0, gtk.MESSAGE_WARNING, gtk.BUTTONS_OK_CANCEL, msg)
        dialog.set_title(_('Burning USB4Butia board...'))
        res = dialog.run()
        dialog.destroy()

        if res == gtk.RESPONSE_OK:
            self.flash()

    def check_message(self, widget=None):
        ver = self.get_version()
        if ver == -1:
            msg = _('Error reading Firmware version.\nTry again or test USB connection...')
            dialog = gtk.MessageDialog(self.parent, 0, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, msg)
        else:
            msg = _('The current version of the Firmware\nis %s') % ver
            dialog = gtk.MessageDialog(self.parent, 0, gtk.MESSAGE_INFO, gtk.BUTTONS_OK, msg)
        dialog.set_title(_('USB4Butia firmware version...'))
        dialog.run()
        dialog.destroy()

    def flash(self):
        i = time.time()

        try:
            arq = platform.machine()
        except:
            print 'Error getting platform info'

        if arq == 'x86_64':
            path = './fsusb/x64/fsusb'
            print 'Use 64bits fsusb'
        elif arq.startswith('arm'):
            path = './fsusb/ARM/fsusb'
            print 'Use ARM fsusb'
        else:
            path = './fsusb/x32/fsusb'
            print 'Use default 32bits fsusb'

        dialog = self.initing()

        print 'Trying --force_program option'
        try:
            proc = subprocess.Popen([path, '--force_program', self.firmware_hex])
        except Exception, err:
            print 'Error in fsusb --force_program:', err
            error = err
            proc = None

        if proc:
            self.wait_proc(proc)
            if proc.returncode == 0:
                self.sucess(int(time.time() - i))
            else:
                print 'Trying --program option'
                try:
                    proc = subprocess.Popen([path, '--program', self.firmware_hex])
                except Exception, err:
                    print 'Error in fsusb --program:', err
                    error = err
                    proc = None
                if proc:
                    self.wait_proc(proc)
                    if (proc.returncode == 0) or (proc.returncode == 1):
                        self.sucess(int(time.time() - i))
                    else:
                        self.unsucess(proc.returncode)
                else:
                    self.unsucess(error)
        else:
            self.unsucess(error)

        dialog.destroy()

    def initing(self):
        msg = _('Burning USB4Butia board...')
        dialog = gtk.MessageDialog(self.parent, 0, gtk.MESSAGE_INFO, gtk.BUTTONS_NONE, msg)
        dialog.set_title(_('Burning...'))
        self.pbar = gtk.ProgressBar()
        content = dialog.get_content_area() 
        content.add(self.pbar)
        self.pbar.show()
        # Run es bloqueante
        #dialog.run()
        dialog.show()
        return dialog

    def progress_timeout(self):
        new_val = self.pbar.get_fraction() + 0.01
        if new_val > 1.0:
            new_val = 0.0
        self.pbar.set_fraction(new_val)

    def wait_proc(self, proc):
        self.pbar.set_fraction(0.0)
        while proc.poll() == None:
            time.sleep(0.1)
            self.progress_timeout()
            while gtk.events_pending():
                gtk.main_iteration()
        self.pbar.set_fraction(1.0)

    def sucess(self, seconds):
        msg = _('The upgrade ends successfully!\nThe process takes %s seconds') % seconds
        dialog = gtk.MessageDialog(self.parent, 0, gtk.MESSAGE_INFO, gtk.BUTTONS_CLOSE, msg)
        dialog.set_title(_('Burning USB4Butia board...'))
        dialog.run()
        dialog.destroy()

    def unsucess(self, err):
        msg = _('The upgrade fails. Try again.\nError: %s') % err
        dialog = gtk.MessageDialog(self.parent, 0, gtk.MESSAGE_ERROR, gtk.BUTTONS_CLOSE, msg)
        dialog.set_title(_('Burning USB4Butia board...'))
        dialog.run()
        dialog.destroy()

    def get_version(self):
        b = usb4butia.USB4Butia(get_modules=False)
        version = b.getFirmwareVersion()
        b.close()
        return version


if __name__ == "__main__":
    f = Flash()
    f.build_window()

