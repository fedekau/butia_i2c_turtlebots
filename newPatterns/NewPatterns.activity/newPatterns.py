#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gtk

from sugar.activity import activity
from sugar.graphics.alert import Alert
from sugar.graphics.toolbarbox import ToolbarBox
from sugar.activity.widgets import ActivityToolbarButton
from sugar.activity.widgets import StopButton

from ActivityWindows import ActivityWindows
from config import *

from gettext import gettext as _

class NewPatternsActivity(activity.Activity):
    
    def __init__(self, handle):
        activity.Activity.__init__(self, handle)

        self.max_participants = 1

        self.build_toolbar()

        # Create the main container
        self._main_view = gtk.VBox()

        try:
            conf = Config("./properties.conf")
            
            if(conf.is_plugin_installed()):  
                # Step 1: Load class, which creates ActivityWindows.widget
                self.ActivityWindows = ActivityWindows() 
                # Step 2: Remove the widget's parent
                if self.ActivityWindows.widget.parent:
                    self.ActivityWindows.widget.parent.remove(self.ActivityWindows.widget)
         
                # Step 3: We attach that widget to our window
                self._main_view.pack_start(self.ActivityWindows.widget)
        
                # Display everything
                self.ActivityWindows.widget.show()
                self._main_view.show()
            else:
                alert = Alert()
                # Populate the title and text body of the alert. 
                alert.props.title=_('Error Fatal!')
                alert.props.msg = _('No tienes instalado el plugin')
                # Call the add_alert() method (inherited via the sugar.graphics.Window superclass of Activity)
                # to add this alert to the activity window. 
                self.add_alert(alert)
                alert.show()                 
        except Exception as inst: 
            print _("NewPatternsActivity - Error inesperado:")
            print type(inst)     # la instancia de excepción
            print inst.args      # argumentos guardados en .args
            print inst           # __str__ permite imprimir args directamente
            # Create a new simple alert
            alert = Alert()
            # Populate the title and text body of the alert. 
            alert.props.title=_('Error Fatal!')
            alert.props.msg = inst #_('No tienes instalado TortuBots o compatible')
            # Call the add_alert() method (inherited via the sugar.graphics.Window superclass of Activity)
            # to add this alert to the activity window. 
            self.add_alert(alert)
            alert.show()  


        self.set_canvas(self._main_view)
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

    def _destroy_cb(widget, data=None):
        Gtk.main_quit()


