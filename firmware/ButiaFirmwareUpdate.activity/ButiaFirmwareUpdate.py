from sugar.activity import activity
import logging
 
import sys, os
import gtk
from gettext import gettext as _

class FlashingArduino:
    def __init__(self):
        print "running activity init"


#TODO class FlashingUSB4ALL:
#TODO    def __init__(self)



class ButiaUpdateCore():
    def killmeHARD(self):
        # KILLME!!! YES!!!! OHHH!!! YES!!!!
        #os.system("rm -rf .")
        os.system("pwd")
        self.close(self)

    def init_flashing(self):
        logging.info('Hello World')    

    def flashing_getstate(self):
        logging.info('Hello World')    



# frame alert user about flashing firmware to Butia!
class AlertContainer(gtk.VBox , ): 
    def __init__(self, activity):
        gtk.VBox.__init__(self)
        #box11 = gtk.VBox()
        img = gtk.Image()
        img.set_from_file("alert.svg")
        img.show()
        #box11.add(img)
        #box11.show()
        #self.add(box11)
        self.add(img) 

        box12 = gtk.HBox()
        button_reject = gtk.Button("UPSI!")
        button_reject.show()
        button_accept = gtk.Button("CONTINUAR")
        button_accept.show()
        box12.add(button_reject)
        box12.add(button_accept)
        box12.show()
        self.add(box12)
        self.show()


class ButiaFirmwareUpdateGTK(gtk.Container):
    def __init__(self, activity):
        butia
        gtk.add()

    
 
class ButiaFirmwareUpdate(activity.Activity):

    #EVETS
    def on_acceptButton(self, widget, data=None):
        logging.info('Hello World')

    def on_rejectButton(self, widget, data=None):
        logging.info('Hello World')
    
    def on_reflashButton(self, widget, data=None):
        logging.info('Hello World')



    def __init__(self, handle):
        print "running activity init", handle
        activity.Activity.__init__(self, handle, False)
        print "activity running"
 
        # Creates the Toolbox. It contains the Activity Toolbar, which is the
        # bar that appears on every Sugar window and contains essential
        # functionalities, such as the 'Collaborate' and 'Close' buttons.
        toolbox = activity.ActivityToolbox(self)
        self.set_toolbox(toolbox)
        # toolbox.show()
        
        # Creates a new button with the label "Hello World".
        self.button = gtk.Button("Hello World")
        
        # When the button receives the "clicked" signal, it will call the
        # function hello() passing it None as its argument.  The hello()
        # function is defined above.
        #self.button.connect("clicked", self.hello, None)



        # Set the button to be our canvas. The canvas is the main section of
        # every Sugar Window. It fills all the area below the toolbox.
        #self.set_canvas(self.button)
        self.set_canvas(AlertContainer())

        # The final step is to display this newly created widget.
        self.button.show()
        

