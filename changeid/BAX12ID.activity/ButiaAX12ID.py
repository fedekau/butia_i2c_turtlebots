import logging
import shlex
import subprocess
import commands
import sys, os
import time
import gtk
import butiaAPI
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
        
        #combo = gtk.ComboBox()

        img.set_from_file("activity/wall.svg")
        img.show()

        self.add(fcom)
        self.add(fbcidl)
        self.add(fbcidr)
        self.add(fbcid)
        self.add(fim)        
        
		#Boton change ID left motor
        button_acceptl = gtk.Button(_("Change ID (LEFT motor)"))
        #button_acceptl.set_size_request(100, 100)
        button_acceptl.connect("clicked", self.warning_messageIDL)
        #Boton change ID right motor
        button_acceptr = gtk.Button(_("Change ID (RIGHT motor)"))
        #button_acceptr.set_size_request(100, 100)
        button_acceptr.connect("clicked", self.warning_messageIDR)
        #Boton change ID motor
        button_accept = gtk.Button(_("Change ID"))
        #button_acceptr.set_size_request(100, 100)
        button_accept.connect("clicked", self.warning_messageID)

        
        #bcb = ComboID()


        # ID combobox
        l = gtk.ListStore(str)
        combo = gtk.ComboBox(l)
        cell = gtk.CellRendererText()
        combo.pack_start(cell, True)
        combo.add_attribute(cell, 'text', 0)
        combo.append_text('Select ID:')
        for i in range(0, 253):
            combo.append_text(str(i))
        combo.set_active(0)

        def changed_cb(self):
            #self.sel = combo.get_active()
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
        
        fbcidl.put(button_acceptl, 10, 20)
        fbcidr.put(button_acceptr, 10, 20)
        fbcid.put(button_accept, 10, 20)
        fcom.put(combo, 10, 20)
        fim.put(img, 1, 20)

        vbox.add(fbcidl)
        vbox.add(fbcidr)
        vbox.add(fbcid)
        vbox.add(fcom)
        box.add(vbox)
        box.add(fim)
        box.show_all()

        self.set_canvas(box)
#	return box
  
	#levantar bobot
    def bobot_launch(self):

        print 'Initialising butia...'
        output = commands.getoutput('ps -ax | grep lua')
        if 'bobot-server' in output:
            print 'bobot is alive!'
        else:
            try:
                print 'creating bobot'
                self.bobot = subprocess.Popen(['./lua', 'bobot-server.lua'], cwd='./lib/butia_support')
            except:
                print 'ERROR creating bobot'

        time.sleep(1)

        self.butia = butiaAPI.robot()

        self.modules = self.butia.get_modules_list()

        if (self.modules != []):
            print self.modules
        else:
            print _('Butia robot was not detected')



		  #Mensaje change id left
    def warning_messageIDL(self, widget):
        msg = _('Please connect ONLY the LEFT motor to the board, and the power to this motor.\nNot disconnect the board and not close this activity.\nDo you want to continue?')
        dialog = gtk.MessageDialog(self, 0, gtk.MESSAGE_WARNING, gtk.BUTTONS_OK_CANCEL, msg)
        dialog.set_title(_('Changing motor ID...'))
        res = dialog.run()
        dialog.destroy()


        self.bobot_launch()

        if res == gtk.RESPONSE_OK:
            #dialog = self.initing()
            self.butia.write_info('254', '3', '1' )
            if self.butia:
                self.butia.close()
                self.butia.closeService()
            if self.bobot:
                self.bobot.kill()
				
        elif res ==  gtk.RESPONSE_CANCEL:
            pass
		  
		  #mensaje change id right
    def warning_messageIDR(self, widget):
        msg = _('Please connect ONLY the RIGHT motor to the board, and the power to this motor.\nNot disconnect the board and not close this activity.\nDo you want to continue?')
        dialog = gtk.MessageDialog(self, 0, gtk.MESSAGE_WARNING, gtk.BUTTONS_OK_CANCEL, msg)
        dialog.set_title(_('Changing motor ID...'))
        res = dialog.run()
        dialog.destroy()

        self.bobot_launch()

        if res == gtk.RESPONSE_OK:
            
            #dialog = self.initing()
				#prender led (broadcast, reg, value)
            self.butia.write_info('254', '3', '2' )
            #self.butia.write_info('254', '25', '1' )
            if self.butia:
                self.butia.close()
                self.butia.closeService()
            if self.bobot:
                self.bobot.kill()

        elif res ==  gtk.RESPONSE_CANCEL:
            pass

		  #mensaje change id
    def warning_messageID(self, widget):
        msg = _('Please connect to the board ONLY the motor or motors that you want to change it id.\nYour motor''s new ID will be ' + str(ButiaAX12ID.sel) + '\nNot disconnect the board and not close this activity.\nDo you want to continue?')
        dialog = gtk.MessageDialog(self, 0, gtk.MESSAGE_WARNING, gtk.BUTTONS_OK_CANCEL, msg)
        dialog.set_title(_('Changing motor ID...'))
        res = dialog.run()
        dialog.destroy()

        self.bobot_launch()

        if res == gtk.RESPONSE_OK:
            self.butia.write_info('254', '3', str(ButiaAX12ID.sel) )
            if self.butia:
                self.butia.close()
                self.butia.closeService()
            if self.bobot:
                self.bobot.kill()

        elif res ==  gtk.RESPONSE_CANCEL:
            pass
