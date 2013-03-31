#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import commands
import time
import gtk
from pybot import pybot_client

from sugar.activity import activity
from sugar.activity.widgets import ActivityToolbarButton
from sugar.graphics.toolbarbox import ToolbarBox
from sugar.activity.widgets import StopButton
from sugar.graphics.toolbarbox import ToolbarButton

from gettext import gettext as _

class ButiaAX12ID(activity.Activity):

    def __init__(self, handle):
        activity.Activity.__init__(self, handle)
        #disable share
        self.max_participants = 1
        self.sel = -1
        self.build_toolbar()
        self.build_canvas()
        self.show_all()
        self.pybot_launch()

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

        # Activity stop button
        stop_button = StopButton(self)
        toolbox.toolbar.insert(stop_button, -1)
        stop_button.show()

        self.set_toolbox(toolbox)
        toolbox.show()
        
    # aux function for combobox selection
    def changed_cb(self, combo):
        index = combo.get_active()
        self.sel = index - 1

    def build_canvas(self):
        #The canvas is the main section of every Sugar Window.
        # It fills all the area below the toolbox.

        box = gtk.HBox()
        vbox = gtk.VBox()
        img = gtk.Image()
        fbcidl = gtk.Fixed()
        fbcidr = gtk.Fixed()
        fbcid = gtk.Fixed()
        fim = gtk.Fixed()
        fcom = gtk.Fixed()
        
        img.set_from_file("activity/wall.svg")
        img.show()
        
		#Boton change ID left motor
        button_acceptl = gtk.Button(_('Change ID (%s motor)') % _('LEFT'))
        button_acceptl.connect("clicked", self.warning_messageIDL)
        #Boton change ID right motor
        button_acceptr = gtk.Button(_('Change ID (%s motor)') % _('RIGHT'))
        button_acceptr.connect("clicked", self.warning_messageIDR)
        #Boton change ID motor
        button_accept = gtk.Button(_("Change ID (CUSTOM)"))
        button_accept.connect("clicked", self.warning_messageID)
        # Combo change custom ID
        l = gtk.ListStore(str)
        combo = gtk.ComboBox(l)
        cell = gtk.CellRendererText()
        combo.pack_start(cell, True)
        combo.add_attribute(cell, 'text', 0)
        combo.append_text(_('Select ID:'))
        #list of available IDs
        for i in range(0, 253):
            combo.append_text(str(i))
        combo.set_active(0)
        combo.connect('changed', self.changed_cb)        
        self.connect("destroy", self.on_destroy)

        #Button alignment 
        fbcidl.put(button_acceptl, 10, 5)
        fbcidr.put(button_acceptr, 10, -100)
        fcom.put(combo, 10, 5)
        fbcid.put(button_accept, 10, -100)
        fim.put(img, 1, 20)

        vbox.add(fbcidl)
        vbox.add(fbcidr)
        vbox.add(fcom)
        vbox.add(fbcid)
        box.add(vbox)
        box.add(fim)
        box.show_all()
        self.set_canvas(box)

    def pybot_launch(self):
        output = commands.getoutput('ps -ax | grep python')
        if 'pybot_server.py' in output:
            print 'Pybot is alive!'
        else:
            try:
                print 'creating Pybot server'
                self.bobot = subprocess.Popen(['python', 'pybot_server.py'], cwd='./pybot')
            except:
                print 'ERROR creating Pybot server'
        # Sure that bobot is running
        time.sleep(2)
        self.butia = pybot_client.robot()
        time.sleep(1)

    #main function, change id
    def change_id(self, idn, msg):
        msg = msg + _("Not disconnect the board and not close this activity.\nDo you want to continue?")
        dialog = gtk.MessageDialog(self, 0, gtk.MESSAGE_WARNING, gtk.BUTTONS_OK_CANCEL, msg)
        dialog.set_title(_('Changing motor ID...'))
        res = dialog.run()
        dialog.destroy()
        if res == gtk.RESPONSE_OK:
            self.butia.write_info('254', '3', str(idn))
            time.sleep(1)
            check = self.butia.write_info(str(idn), '25', '1')
            time.sleep(1)
            self.butia.write_info(str(idn), '25', '0')
            #print check
            if check == 1:
                msg1 = _('ID Change CORRECT.\nYour new motor ID is %s.') % str(idn)
                dialog1 = gtk.MessageDialog(self, 0, gtk.MESSAGE_INFO, gtk.BUTTONS_OK, msg1)
                dialog1.set_title(_('Information'))
                dialog1.run()
                dialog1.destroy()
            else:
                msg1 = _('ID Change ERROR\nPlease check board and motor connections.')
                dialog1 = gtk.MessageDialog(self, 0, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, msg1)
                dialog1.set_title(_('Information'))
                dialog1.run()
                dialog1.destroy()

	#change left id message
    def warning_messageIDL(self, widget):
        m = _("Please connect ONLY the %s motor to the board, and the power to this motor.\n") % _('LEFT')
        self.change_id('1', m)
    
    #change right id message
    def warning_messageIDR(self, widget):
        m = _("Please connect ONLY the %s motor to the board, and the power to this motor.\n") % _('RIGHT')
        self.change_id('2', m)

    #change custom id message
    def warning_messageID(self, widget):
        if self.sel == -1:
            msg = _('You must select an ID in the combo.')
            dialog = gtk.MessageDialog(self, 0, gtk.MESSAGE_INFO, gtk.BUTTONS_OK, msg)
            dialog.set_title(_('Information'))
            dialog.run()
            dialog.destroy()
        else:
            m = _("Please connect to the board ONLY the motor or motors that you want to change it ID.\n\
Your motor's new ID will be %s.\n")
            m = m % str(self.sel)
            self.change_id(str(self.sel), m)

    def on_destroy(self, widget):
        gtk.main_quit()
        if self.butia:
            self.butia.closeService()
            self.butia.close()

