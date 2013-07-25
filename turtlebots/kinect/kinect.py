import gtk
import sys, os
import logging
from gettext import gettext as _
from plugins.plugin import Plugin
from TurtleArt.tapalette import make_palette, special_block_colors
from TurtleArt.talogo import primitive_dictionary, logoerror
from TurtleArt.taconstants import BOX_COLORS
from TurtleArt.tautils import convert

from openni import *
import threading

COLOR_NOTPRESENT = ["#A0A0A0","#808080"] 
COLOR_PRESENT = ["#00FF00","#008000"] 
 

class Kinect(Plugin):

  def __init__(self, parent):
    self.parent = parent
    self.handPresent = False
    self.lastHandPresent = False
    self.xHand = 0
    self.yHand = 0
    self.zHand = 0

    self.kinectBlocks = ['xKinect', 'yKinect', 'zKinect']

    self.pollrun = True
    self.kinectThread=None
    self.paletteThread=None

  def setup(self):
    palette = make_palette('kinect',  # the name of your palette
                           colors=["#00FF00", "#00A000"],
                           help_string=_('Palette of kinect sensor'))

    primitive_dictionary['xKinect'] = self._prim_xPos
    palette.add_block('xKinect',
                      style='box-style',
                      label=_('hand x-axis'),
                      value_block=True,
                      prim_name='xKinect',
                      help_string=_('returns the hand x-axis position as a number between -540 and 540'))
    self.parent.lc.def_prim('xKinect', 0, lambda self:
                         primitive_dictionary['xKinect']())
    special_block_colors['xKinect'] = COLOR_NOTPRESENT[:]

    primitive_dictionary['yKinect'] = self._prim_yPos
    palette.add_block('yKinect',
                      style='box-style',
                      label=_('hand y-axis'), 
                      value_block=True,
                      prim_name='yKinect', 
                      help_string=_('returns the hand y-axis position as a number between -400 and 400'))
    self.parent.lc.def_prim('yKinect', 0, lambda self:
                         primitive_dictionary['yKinect']())
    special_block_colors['yKinect'] = COLOR_NOTPRESENT[:]

    primitive_dictionary['zKinect'] = self._prim_zPos
    palette.add_block('zKinect',
                      style='box-style',
                      label=_('hand z-axis'),
                      value_block=True,
                      prim_name='zKinect',
                      help_string=_('returns the hand z-axis position as a number between 420 and 1200'))
    self.parent.lc.def_prim('zKinect', 0, lambda self:
                         primitive_dictionary['zKinect']())
    special_block_colors['zKinect'] = COLOR_NOTPRESENT[:]

    self.kinectThread=threading.Timer(0, self.startTracking)
    self.kinectThread.start()
    self.paletteThread=threading.Timer(0, self.paletteCheck)
    self.paletteThread.start()

  def quit(self):
    """ cleanup is called when the activity is exiting. """
    self.pollrun = False
    self.kinectThread.cancel()
      
  def gesture_detected(self,src, gesture, id, end_point):
    self.hands_generator.start_tracking(end_point)

  # TODO check this
  def gesture_progress(self,src, gesture, point, progress): pass

  def create(self,src, id, pos, time):
    print 'Create ', id, pos
    self.handPresent = True

  def update(self,src, id, pos, time):
    print 'Update ', id, pos    
    self.xHand = pos[0]
    self.yHand = pos[1]
    self.zHand = pos[2]

  def destroy(self,src, id, time):
    print 'Destroy ', id
    self.handPresent = False
    self.xHand = -1
    self.yHand = -1
    self.zHand = -1

  def _prim_xPos(self):
    return self.xHand

  def _prim_yPos(self):
    return self.yHand

  def _prim_zPos(self):
    return self.zHand

  def startTracking(self):
    print("Start tracking")
    try:
      self.context = Context()
      self.context.init()

      self.depth_generator = DepthGenerator()
      self.depth_generator.create(self.context)
      #TODO check if parametrs ok
      self.depth_generator.set_resolution_preset(RES_VGA)
      self.depth_generator.fps = 30

      self.gesture_generator = GestureGenerator()
      self.gesture_generator.create(self.context)
      self.gesture_generator.add_gesture('Wave')

      self.hands_generator = HandsGenerator()
      self.hands_generator.create(self.context)

      self.gesture_generator.register_gesture_cb(self.gesture_detected, self.gesture_progress)
      self.hands_generator.register_hand_cb(self.create, self.update, self.destroy)  
      self.context.start_generating_all()

      self.kinectThread=threading.Timer(1, self.track_poll)
      self.kinectThread.start()
    except:
        print("Exception in start tracking")
        self.pollrun = False


  def track_poll(self):
    if self.pollrun:
      self.context.wait_any_update_all()  
      self.kinectThread=threading.Timer(0.01, self.track_poll)
      self.kinectThread.start()
    else:
      print("Ending track poll")

  def paletteCheck(self):
    if self.pollrun:
      if not self.handPresent == self.lastHandPresent:
        self.lastHandPresent = self.handPresent
        print("update palette!")
        self.updatePalette(self.handPresent)
      self.paletteThread=threading.Timer(2, self.paletteCheck)
      self.paletteThread.start()

  def updatePalette(self, hand):
    for blk in self.parent.block_list.list:
      if blk.type in ['proto', 'block']:
        if blk.name in self.kinectBlocks:      
          if hand:
            special_block_colors[blk.name] = COLOR_PRESENT[:]
          else:
            special_block_colors[blk.name] = COLOR_NOTPRESENT[:]
          blk.refresh()






