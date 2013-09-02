#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import subprocess
import commands
import time
import gtk
import ConfigParser
import gettext
from pybot import pybot_client

from gettext import gettext as _

class AX12():

    def __init__(self, parent=None):
        self.parent = parent
        self.pybot_launch()

    def build_window(self):
        self.get_translations()
        win = gtk.Window()
        win.set_title(_('AX-12 ID Changer'))
        win.connect('delete_event', self._quit)
        canvas = self.build_canvas()
        win.add(canvas)
        win.show()
        gtk.main()

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
        return box

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
        dialog = gtk.MessageDialog(self.parent, 0, gtk.MESSAGE_WARNING, gtk.BUTTONS_OK_CANCEL, msg)
        dialog.set_title(_('Changing motor ID...'))
        mod_list = self.butia.getModulesList()
        print 'Module list %s' % mod_list
        res = dialog.run()
        dialog.destroy()
        if res == gtk.RESPONSE_OK:
            #get the listi
            listi = self.butia.getListi()
            print 'This USB4Butia have this modules: %s' % listi
            if 'ax' in listi:
                # broadcast to set ID (3)
                print 'Broadcast to set ID number %s...' % str(idn)
                check = self.butia.writeInfo('254', '3', str(idn))
                print 'WriteInfo returns %s' % check
                time.sleep(1)
                # turn LED on
                print 'Turn motor LED on...'
                check = self.butia.writeInfo(str(idn), '25', '1')
                print 'Turn motor LED on returns %s' % check
                time.sleep(1)
                # turn LED off
                print 'Turn motor LED off...'
                self.butia.writeInfo(str(idn), '25', '0')
                print 'Turn motor LED off returns %s' % check
                #print check
                if check == 0:
                    msg1 = _('ID Change CORRECT.\nYour new motor ID is %s.') % str(idn)
                    dialog1 = gtk.MessageDialog(self.parent, 0, gtk.MESSAGE_INFO, gtk.BUTTONS_OK, msg1)
                else:
                    msg1 = _('ID Change ERROR\nPlease check board and motor connections.')
                    dialog1 = gtk.MessageDialog(self.parent, 0, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, msg1)
                dialog1.set_title(_('Information'))
                dialog1.run()
                dialog1.destroy()
            else:
                if (listi == []):
                    print 'empty listi - usb4butia disconnected?'
                    msg1 = _('We have an empty LISTI. That can means that board is disconnected. Check it.')
                else:
                    print 'ax module is not present'
                    msg1 = _('The ax module is not present. Please update the USB4Butia Firmware.')
                dialog1 = gtk.MessageDialog(self.parent, 0, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, msg1)
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
            dialog = gtk.MessageDialog(self.parent, 0, gtk.MESSAGE_INFO, gtk.BUTTONS_OK, msg)
            dialog.set_title(_('Information'))
            dialog.run()
            dialog.destroy()
        else:
            m = _("Please connect to the board ONLY the motor or motors that you want to change it ID.\n\
Your motor's new ID will be %s.\n")
            m = m % str(self.sel)
            self.change_id(str(self.sel), m)

    def _quit(self, win, e):
        print 'Quit'
        gtk.main_quit()
        if self.butia:
            print 'Closing PyBot...'
            self.butia.closeService()
            self.butia.close()
        exit()

if __name__ == "__main__":
    ax = AX12()
    ax.build_window()

