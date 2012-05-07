#!/usr/bin/env python
# Copyright (c) 2011 Alan Aguiar, <alanjas@hotmail.com>
# Copyright (c) 2011 Aylen Ricca, <ar18_90@hotmail.com>
# Copyright (c) 2011 Rodrigo Dearmas, <piegrande46@hotmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import gtk
import sys, os
import logging
from gettext import gettext as _
from plugins.plugin import Plugin
from TurtleArt.tapalette import make_palette
from TurtleArt.talogo import primitive_dictionary, logoerror
from TurtleArt.taconstants import BOX_COLORS
from TurtleArt.tautils import convert

sys.path.insert(0, os.path.abspath('./plugins/followme/lib'))

try:
    import pygame
    import pygame.camera as pycam
except ImportError:
    pass

COLOR_NOTPRESENT = ["#A0A0A0","#808080"]
_logger = logging.getLogger('turtleart-activity followme plugin')


class Followme(Plugin):

    def __init__(self, parent):
        self.parent = parent
        self.cam_present = False
        self.cam_on = False
        self.colorc = (255, 255, 255)
        self.threshold = (25, 25, 25)
        self.pixels_min = 10
        self.pixels = 0
        self.calibrations = {}
        try:
            pygame.init()
            pycam.init()
            self.lcameras = pycam.list_cameras()
            if self.lcameras:
                self.cam = pycam.Camera(self.lcameras[0], (320,240), 'RGB')
                self.capture = pygame.surface.Surface((320,240))
                self.mask = None
                self.connected = None
                self.cam_present = True
            else:
                print _('The camera was not found.')
        except:
            print _('Error on the initialization of the camera.')

    def dynamicLoadBlockColors(self):
        if not(self.cam_present):
            BOX_COLORS['followRGB'] = COLOR_NOTPRESENT
            BOX_COLORS['follow'] = COLOR_NOTPRESENT
            BOX_COLORS['threshold'] = COLOR_NOTPRESENT
            BOX_COLORS['pixels_min'] = COLOR_NOTPRESENT
            BOX_COLORS['calibrate'] = COLOR_NOTPRESENT
            BOX_COLORS['xposition'] = COLOR_NOTPRESENT
            BOX_COLORS['yposition'] = COLOR_NOTPRESENT
            BOX_COLORS['pixels'] = COLOR_NOTPRESENT

    def setup(self):

        self.dynamicLoadBlockColors()

        palette = make_palette('FollowMe', colors=["#00FF00","#008000"],
                                help_string=_('FollowMe'))

        primitive_dictionary['followRGB'] = self.prim_followRGB
        palette.add_block('followRGB',
                        style='basic-style-3arg',
                        label=[('FollowMe  G'), ('R'), ('B')],
                        default=[255, 255, 255],
                        help_string=_('follow a RGB color'),
                        prim_name='followRGB')
        self.parent.lc.def_prim('followRGB', 3, lambda self, x, y, z:
                        primitive_dictionary['followRGB'](x, y, z))

        primitive_dictionary['threshold'] = self.prim_threshold
        palette.add_block('threshold',
                        style='basic-style-3arg',
                        label=[('Threshold  G'), ('R'), ('B')],
                        default=[25, 25, 25],
                        help_string=_('set a threshold for a RGB color'),
                        prim_name='threshold')
        self.parent.lc.def_prim('threshold', 3, lambda self, x, y, z:
                        primitive_dictionary['threshold'](x, y, z))


        primitive_dictionary['savecalibration'] = self._prim_savecalibration
        palette.add_block('savecalibration1',
                          style='basic-style',
                          label=_('save calibration 1'),
                          prim_name='savecalibration1',
                          help_string=_('stores numeric value in Variable 1'))
        self.parent.lc.def_prim('savecalibration1', 0,
                             lambda self: primitive_dictionary['savecalibration'](
                'calibration1', None))

        primitive_dictionary['savecalibration'] = self._prim_savecalibration
        palette.add_block('savecalibration2',
                          style='basic-style',
                          label=_('save calibration 2'),
                          prim_name='savecalibration2',
                          help_string=_('stores numeric value in Variable 2'))
        self.parent.lc.def_prim('savecalibration2', 0,
                             lambda self: primitive_dictionary['savecalibration'](
                'calibration2', None))

        primitive_dictionary['savecalibration'] = self._prim_savecalibration
        palette.add_block('savecalibrationN',
                          style='basic-style-1arg',
                          label=_('save calibration'),
                          prim_name='savecalibrationN',
                          default='3',
                          help_string=_('stores numeric value in Variable 2'))
        self.parent.lc.def_prim('savecalibrationN', 1,
                             lambda self, x: primitive_dictionary['savecalibration'](
                'calibration', x))


        primitive_dictionary['calibration'] = self._prim_calibration
        palette.add_block('calibration1',
                        style='box-style',
                        label=_('calibration 1'),
                        help_string=_('return calibration 1'),
                        value_block=True,
                        prim_name='calibration1')
        self.parent.lc.def_prim('calibration1', 0, lambda self:
                        primitive_dictionary['calibration']('calibration1', None))

        primitive_dictionary['calibration'] = self._prim_calibration
        palette.add_block('calibration2',
                        style='box-style',
                        label=_('calibration 2'),
                        help_string=_('return calibration 2'),
                        value_block=True,
                        prim_name='calibration2')
        self.parent.lc.def_prim('calibration2', 0, lambda self:
                        primitive_dictionary['calibration']('calibration2', None))

        primitive_dictionary['calibration'] = self._prim_calibration
        palette.add_block('calibration',
                          style='number-style-1strarg',
                          label=_('calibration'),
                          prim_name='calibration',
                          default=3,
                          help_string=_('named variable '))
        self.parent.lc.def_prim('calibration', 1,
                             lambda self, x: primitive_dictionary['calibration']('calibration', x))

        primitive_dictionary['xposition'] = self.prim_xposition
        palette.add_block('xposition',
                        style='box-style',
                        label=_('x position'),
                        help_string=_('return x position'),
                        value_block=True,
                        prim_name='xposition')
        self.parent.lc.def_prim('xposition', 0, lambda self:
                        primitive_dictionary['xposition']())

        primitive_dictionary['yposition'] = self.prim_yposition
        palette.add_block('yposition',
                        style='box-style',
                        label=_('y position'),
                        help_string=_('return y position'),
                        value_block=True,
                        prim_name='yposition')
        self.parent.lc.def_prim('yposition', 0, lambda self:
                        primitive_dictionary['yposition']())

        primitive_dictionary['pixels'] = self.prim_pixels
        palette.add_block('pixels',
                        style='box-style',
                        label=_('pixels'),
                        help_string=_('return the number of pixels of the biggest blob'),
                        value_block=True,
                        prim_name='pixels')
        self.parent.lc.def_prim('pixels', 0, lambda self:
                        primitive_dictionary['pixels']())

        primitive_dictionary['follow'] = self.prim_follow
        palette.add_block('follow',
                        style='basic-style-1arg',
                        label=('FollowMe '),
                        default=0,
                        help_string=_('follow a turtle color'),
                        prim_name='follow')
        self.parent.lc.def_prim('follow', 1, lambda self, x:
                        primitive_dictionary['follow'](x))

        primitive_dictionary['pixels_min'] = self.prim_pixels_min
        palette.add_block('pixels_min',
                        style='basic-style-1arg',
                        label=('Pixels Min'),
                        default=10,
                        help_string=_('set the minimal number of pixels to follow'),
                        prim_name='pixels_min')
        self.parent.lc.def_prim('pixels_min', 1, lambda self, x:
                        primitive_dictionary['pixels_min'](x))


    def stop(self):
        if (self.cam_present and self.cam_on):
            self.cam.stop()
            self.cam_on = False

    def quit(self):
        if (self.cam_present and self.cam_on):
            self.cam.stop()
            self.cam_on = False
            
    def clear(self):
        pass

    def prim_followRGB(self, R, G, B):
        if type(R) == float:
            R = int(R)
        if type(G) == float:
            G = int(G)
        if type(B) == float:
            B = int(B)

        if (R < 0) or (R > 255):
            R = 255
        if (G < 0) or (G > 255):
            G = 255
        if (B < 0) or (B > 255):
            B = 255
        self.colorc = (R, G, B)

    def prim_follow(self, x):
        if type(x) == float:
            x = int(x)
        elif type(x) == str:
            self.colorc = self.str_to_tuple(x)
        elif type(x) == int:
            if x == 0:
                self.colorc = (255, 0, 0)
            elif x == 10:
                self.colorc = (255, 128, 0)
            elif x == 20:
                self.colorc = (255, 255, 0)
            elif x == 30:
                self.colorc = (0, 255, 0)
            elif x == 40:
                self.colorc = (0, 255, 128)
            elif x == 50:
                self.colorc = (0, 255, 255)
            elif x == 60:
                self.colorc = (0, 128, 255)
            elif x == 70:
                self.colorc = (0, 0, 255)
            elif x == 80:
                self.colorc = (128, 0, 255)
            elif x == 90:
                self.colorc = (255, 0, 255)
            elif x == -9998:
                self.colorc = (255, 255, 255)
            elif x == -9999:
                self.colorc = (0, 0, 0)
        else:
            self.colorc = (255, 255, 255)
            
    def prim_threshold(self, R, G, B):
        if type(R) == float:
            R = int(R)
        if type(G) == float:
            G = int(G)
        if type(B) == float:
            B = int(B)

        if (R < 0) or (R > 255):
            R = 25
        if (G < 0) or (G > 255):
            G = 25
        if (B < 0) or (B > 255):
            B = 25
        self.threshold = (R, G, B)
    
    def prim_pixels_min(self, x):
        if type(x) == float:
            x = int(x)
        if x < 0:
            x = 1
        self.pixels_min = x

    def calibrate(self):
        self.colorc = (255, 255, 255)
        if self.cam_present:
            if not(self.cam_on):
                try:
                    self.cam.start()
                    self.cam_on = True
                except:
                    pass
            if self.cam_on:
                self.screen = pygame.display.set_mode((1200,900))
                self.clock = pygame.time.Clock()
                self.clock.tick(10)
                self.run = True
                while self.run:
                    while gtk.events_pending():
                        gtk.main_iteration()
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            self.run = False
                        # click o tecla
                        elif event.type == 3:
                            self.run = False
                    self.capture = self.cam.get_image(self.capture)
                    self.capture = pygame.transform.flip(self.capture, True, False)
                    self.screen.blit(self.capture, (0,0))
                    rect = pygame.draw.rect(self.screen, (255,0,0), (100,100,50,50), 4)
                    self.colorc = pygame.transform.average_color(self.capture, rect)
                    self.screen.fill(self.colorc, (320,240,100,100))
                    pygame.display.flip()
                self.screen = pygame.display.quit()
        
        return (self.colorc[0], self.colorc[1], self.colorc[2])

    def prim_xposition(self):
        if self.cam_present:
            if not(self.cam_on):
                try:
                    self.cam.start()
                    self.cam_on = True
                except:
                    return (-1)
            self.capture = self.cam.get_image(self.capture)
            self.mask = pygame.mask.from_threshold(self.capture, self.colorc,
                                                self.threshold)
            self.connected = self.mask.connected_component()
            if (self.connected.count() > self.pixels):
                centroid = self.mask.centroid()
                return (320 - centroid[0])
            else:
                return (-1)
        else:
            return (-1)

    def prim_yposition(self):
        if self.cam_present:
            if not(self.cam_on):
                try:
                    self.cam.start()
                    self.cam_on = True
                except:
                    return (-1)
            self.capture = self.cam.get_image(self.capture)
            self.mask = pygame.mask.from_threshold(self.capture, self.colorc,
                                                self.threshold)
            self.connected = self.mask.connected_component()
            if (self.connected.count() > self.pixels):
                centroid = self.mask.centroid()
                return (240 - centroid[1])
            else:
                return (-1)
        else:
            return (-1)

    def prim_pixels(self):
        if self.cam_present:
            if not(self.cam_on):
                try:
                    self.cam.start()
                    self.cam_on = True
                except:
                    return (-1)
            self.capture = self.cam.get_image(self.capture)
            self.mask = pygame.mask.from_threshold(self.capture, self.colorc,
                                                self.threshold)
            self.connected = self.mask.connected_component()
            return self.connected.count()
        else:
            return (-1)


    def _prim_savecalibration(self, name, x):
        c = self.calibrate()
        if x is not None:
            if type(convert(x, float, False)) == float:
                if int(float(x)) == x:
                    x = int(x)
            name = name + str(x)
        s = str(c[0]) + ', ' + str(c[1]) + ', ' + str(c[2])
        self.calibrations[name] = s
        #self.tw.lc.update_label_value(name, val)


    def _prim_calibration(self, name, x):
        if x is not None:
            if type(convert(x, float, False)) == float:
                if int(float(x)) == x:
                    x = int(x)
            name = name + str(x)
        if self.calibrations.has_key(name):
            return self.calibrations[name]
        else:
            raise logoerror('#empty calibration#')

    def str_to_tuple(self, x):
        try:
            t = x.split(',')
            return (int(t[0]), int(t[1]), int(t[2]))
        except:
            raise logoerror('#error in string convertion#')


