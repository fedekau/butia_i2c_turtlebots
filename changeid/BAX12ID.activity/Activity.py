#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gtk

from sugar.activity import activity
from sugar.activity.widgets import ActivityToolbarButton
from sugar.graphics.toolbarbox import ToolbarBox
from sugar.activity.widgets import StopButton

from ButiaAX12ID import AX12

class ButiaAX12ID(activity.Activity):

    def __init__(self, handle):
        activity.Activity.__init__(self, handle)
        #disable share
        self.max_participants = 1
        self.sel = -1
        self.build_toolbar()
        ax = AX12(self)
        canvas = ax.build_canvas()
        self.set_canvas(canvas)
        self.show_all()

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

