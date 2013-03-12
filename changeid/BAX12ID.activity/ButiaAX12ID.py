import logging
import shlex
import subprocess
import commands
import sys, os
import time
import gtk
from pybot import pybot_client
from gettext import gettext as _


from sugar.activity import activity
from sugar.graphics.toolbarbox import ToolbarBox
from sugar.graphics.toolbutton import ToolButton
from sugar.activity.widgets import ActivityToolbarButton
from sugar.activity.widgets import StopButton
from sugar.graphics.toolbarbox import ToolbarButton

class ButiaAX12ID(activity.Activity):

    sel = ""


    def __init__(self, handle):
        activity.Activity.__init__(self, handle)
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

        self.add(fcom)
        self.add(fbcidl)
        self.add(fbcidr)
        self.add(fbcid)
        self.add(fim)        
        
		#Boton change ID left motor
        button_acceptl = gtk.Button(_("Change ID (LEFT motor)"))
        button_acceptl.connect("clicked", self.warning_messageIDL)
        #Boton change ID right motor
        button_acceptr = gtk.Button(_("Change ID (RIGHT motor)"))
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
        combo.append_text('Select ID:')
        #list of available IDs
        for i in range(0, 253):
            combo.append_text(str(i))
        combo.set_active(0)
        def changed_cb(self):
            model = combo.get_model()
            index = combo.get_active()
            if index:
                ButiaAX12ID.sel = model[index][0]
            return
        combo.connect('changed', changed_cb)
        
        fbcidl.add(button_acceptl)
        fbcidr.add(button_acceptr)
        fbcid.add(button_accept)
        fcom.add(combo)
        


###############################################################################
######################HACER LOS LAYOUTS SIZEABLES##############################
###############################################################################
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
                self.bobot = subprocess.Popen(['python', 'pybot_server.py'], cwd='./plugins/butia/pybot')
            except:
                print 'ERROR creating Pybot server'

        # Sure that bobot is running
        time.sleep(2)

        self.butia = pybot_client.robot()

    
	#change left id message
    def warning_messageIDL(self, widget):
        msg = _('Please connect ONLY the LEFT motor to the board, and the power to this motor.\nNot disconnect the board and not close this activity.\nDo you want to continue?')
        dialog = gtk.MessageDialog(self, 0, gtk.MESSAGE_WARNING, gtk.BUTTONS_OK_CANCEL, msg)
        dialog.set_title(_('Changing motor ID...'))
        res = dialog.run()
        dialog.destroy()
        self.pybot_launch()
        check = 0
        if res == gtk.RESPONSE_OK:
            self.butia.write_info('254', '3', '1' )           
            time.sleep(1)
            check = self.butia.write_info('1', '25', '1')
            time.sleep(1)
            self.butia.write_info('1', '25', '0')
            #print check
            if check == 1:
                msg1 = _('ID Change CORRECT.\nYour new motor ID is 1.')
                dialog1 = gtk.MessageDialog(self, 0, gtk.MESSAGE_INFO, gtk.BUTTONS_OK, msg1)
                dialog1.set_title(_('Information'))
                res1 = dialog1.run()
                dialog1.destroy()
            else:
                msg1 = _('ID Change ERROR\nPlease check board and motor connections.')
                dialog1 = gtk.MessageDialog(self, 0, gtk.MESSAGE_INFO, gtk.BUTTONS_OK, msg1)
                dialog1.set_title(_('Information'))
                res1 = dialog1.run()
                dialog1.destroy()

        elif res ==  gtk.RESPONSE_CANCEL:
            pass
        if self.butia:
            self.butia.close()
            self.butia.closeService()
		  
    
    #change right id message
    def warning_messageIDR(self, widget):
        msg = _('Please connect ONLY the RIGHT motor to the board, and the power to this motor.\nNot disconnect the board and not close this activity.\nDo you want to continue?')
        dialog = gtk.MessageDialog(self, 0, gtk.MESSAGE_WARNING, gtk.BUTTONS_OK_CANCEL, msg)
        dialog.set_title(_('Changing motor ID...'))
        res = dialog.run()
        dialog.destroy()
        self.pybot_launch()
        if res == gtk.RESPONSE_OK:
            self.butia.write_info('254', '3', '2' )
            time.sleep(1)
            check = self.butia.write_info('2', '25', '1')
            time.sleep(1)
            self.butia.write_info('2', '25', '0')
            #print check
            if check == 1:
                msg1 = _('ID Change CORRECT.\nYour new motor ID is 2.')
                dialog1 = gtk.MessageDialog(self, 0, gtk.MESSAGE_INFO, gtk.BUTTONS_OK, msg1)
                dialog1.set_title(_('Information'))
                res1 = dialog1.run()
                dialog1.destroy()
            else:
                msg1 = _('ID Change ERROR\nPlease check board and motor connections.')
                dialog1 = gtk.MessageDialog(self, 0, gtk.MESSAGE_INFO, gtk.BUTTONS_OK, msg1)
                dialog1.set_title(_('Information'))
                res1 = dialog1.run()
                dialog1.destroy()

        elif res ==  gtk.RESPONSE_CANCEL:
            pass

        if self.butia:
            self.butia.close()
            self.butia.closeService()


    #change custom id message
    def warning_messageID(self, widget):
        msg = _('Please connect to the board ONLY the motor or motors that you want to change it id.\nYour motor''s new ID will be ' + str(ButiaAX12ID.sel) + '\nNot disconnect the board and not close this activity.\nDo you want to continue?')
        dialog = gtk.MessageDialog(self, 0, gtk.MESSAGE_WARNING, gtk.BUTTONS_OK_CANCEL, msg)
        dialog.set_title(_('Changing motor ID...'))
        res = dialog.run()
        dialog.destroy()
        self.pybot_launch()
        if res == gtk.RESPONSE_OK:
            self.butia.write_info('254', '3', str(ButiaAX12ID.sel) )
            time.sleep(1)
            check = self.butia.write_info(str(ButiaAX12ID.sel), '25', '1')
            time.sleep(1)
            self.butia.write_info(str(ButiaAX12ID.sel), '25', '0')
            #print check
            if check == 1:
                msg1 = _('ID Change CORRECT.\nYour new motor ID is ' + str(ButiaAX12ID.sel) +'.')
                dialog1 = gtk.MessageDialog(self, 0, gtk.MESSAGE_INFO, gtk.BUTTONS_OK, msg1)
                dialog1.set_title(_('Information'))
                res1 = dialog1.run()
                dialog1.destroy()
            else:
                msg1 = _('ID Change ERROR\nPlease check board and motor connections.')
                dialog1 = gtk.MessageDialog(self, 0, gtk.MESSAGE_INFO, gtk.BUTTONS_OK, msg1)
                dialog1.set_title(_('Information'))
                res1 = dialog1.run()
                dialog1.destroy()

        elif res ==  gtk.RESPONSE_CANCEL:
            pass

        if self.butia:
            self.butia.close()
            self.butia.closeService()
