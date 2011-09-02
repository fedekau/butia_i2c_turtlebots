#!/usr/bin/env python
#Copyright (c) 2011 Alan Aguiar, <alanjas@hotmail.com>
#Copyright (c) 2011 Aylen Ricca, <ar18_90@hotmail.com>
#Copyright (c) 2011 Rodrigo Dearmas, <piegrande46@hotmail.com>
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

import gst
import gtk
from fcntl import ioctl
import sys, os
import logging
from gettext import gettext as _
from plugins.plugin import Plugin
from TurtleArt.tapalette import make_palette
from TurtleArt.talogo import media_blocks_dictionary, primitive_dictionary
from TurtleArt.taconstants import BLACK, WHITE, CONSTANTS, BOX_COLORS

sys.path.insert(0, os.path.abspath('./plugins/followme/lib'))

import pygame
import pygame.camera as pycam

COLOR_NOTPRESENT = ["#A0A0A0","#808080"]
_logger = logging.getLogger('turtleart-activity followme plugin')


class Followme(Plugin):

    def __init__(self, parent):
        self.parent = parent
        self.cam_present = False
        self.cam_on = False
        self.colorc = (255, 255, 255)
        self.threshold = (25, 25, 25)
        try:
            pygame.init()
            pycam.init()
            self.lcameras = pycam.list_cameras()
            if self.lcameras:
                self.cam = pycam.Camera(self.lcameras[0], (320,240), 'RGB')
                self.capture = pygame.surface.Surface((320,240))
                self.cam_present = True
            else:
                print _('The camera was not found.')
        except:
            print _('Error on the initialization of the camera.')

    def dynamicLoadBlockColors(self):
        if not(self.cam_present):
            BOX_COLORS['followRGB'] = COLOR_NOTPRESENT
            BOX_COLORS['follow'] = COLOR_NOTPRESENT
            BOX_COLORS['calibrate'] = COLOR_NOTPRESENT
            BOX_COLORS['xposition'] = COLOR_NOTPRESENT
            BOX_COLORS['yposition'] = COLOR_NOTPRESENT

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

        primitive_dictionary['follow'] = self.prim_follow
        palette.add_block('follow',
                        style='basic-style-1arg',
                        label=('FollowMe '),
                        default=0,
                        help_string=_('follow a turtle color'),
                        prim_name='follow')
        self.parent.lc.def_prim('follow', 1, lambda self, x:
                        primitive_dictionary['follow'](x))

        primitive_dictionary['calibrate'] = self.prim_calibrate
        palette.add_block('calibrate',
                        style='basic-style',
                        label=_('Calibrate'),
                        help_string=_('calibrate a color to follow'),
                        prim_name='calibrate')
        self.parent.lc.def_prim('calibrate', 0, lambda self:
                        primitive_dictionary['calibrate']())

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

    def stop(self):
        if (self.cam_present and self.cam_on):
            self.cam.stop()
            self.cam_on = False

    def quit(self):
        if (self.cam_present and self.cam_on):
            self.cam.stop()
            self.cam_on = False

    def prim_followRGB(self, R, G, B):
        if (self.cam_present and not(self.cam_on)):
            self.cam.start()
            self.cam_on = True
        self.colorc = (R, G, B)

    def prim_follow(self, x):
        if (self.cam_present and not(self.cam_on)):
            self.cam.start()
            self.cam_on = True
        if x == 0:
            self.colorc = (253, 0, 0)
        elif x == 10:
            self.colorc = (253, 129, 0)
        elif x == 20:
            self.colorc = (253, 253, 0)
        elif x == 30:
            self.colorc = (0, 253, 0)
        elif x == 40:
            self.colorc = (0, 253, 129)
        elif x == 50:
            self.colorc = (0, 253, 253)
        elif x == 60:
            self.colorc = (0, 129, 253)
        elif x == 70:
            self.colorc = (0, 0, 253)
        elif x == 80:
            self.colorc = (129, 0, 253)
        elif x == 90:
            self.colorc = (253, 0, 253)
        elif x == -9998:
            self.colorc = (253, 253, 253)
        elif x == -9999:
            self.colorc = (0, 0, 0)
        else:
            self.colorc = (253, 253, 253)

    def prim_calibrate(self):
        if self.cam_present:
            if not(self.cam_on):
                self.cam.start()
                self.cam_on = True
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

    def prim_xposition(self):
        if self.cam_present:
            if not(self.cam_on):
                self.cam.start()
                self.cam_on = True
            self.capture = self.cam.get_image(self.capture)
            mask = pygame.mask.from_threshold(self.capture, self.colorc,
                                                self.threshold)
            connected = mask.connected_component()
            if (connected.count() > 10):
                centroid = mask.centroid()
                return (320 - centroid[0])
            else:
                return (-1)
        else:
            return (-1)

    def prim_yposition(self):
        if self.cam_present:
            if not(self.cam_on):
                self.cam.start()
                self.cam_on = True
            self.capture = self.cam.get_image(self.capture)
            mask = pygame.mask.from_threshold(self.capture, self.colorc,
                                                self.threshold)
            connected = mask.connected_component()
            if (connected.count() > 10):
                centroid = mask.centroid()
                return (240 - centroid[1])
            else:
                return (-1)
        else:
            return (-1)
