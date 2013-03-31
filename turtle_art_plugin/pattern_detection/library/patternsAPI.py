#! /usr/bin/env python
# -*- coding: utf-8 -*-

from ctypes import cdll, create_string_buffer
import os
import time
import threading


class detection:
    multiPatternLib = None
    video = None
    OBJECT_MAX = 30
    exit_th = False
    lock_data = None
    refresh_delay = 0.1
    data_params = None

    def __init__(self, video = "/dev/video0" ):
        self.video = video
        conf = 'v4l2src device=' + self.video
        conf = conf + ' use-fixed-fps=false ! ffmpegcolorspace ! capsfilter '
        conf = conf + 'caps=video/x-raw-rgb,bpp=24 ! identity name=artoolkit ! fakesink'
        os.environ['ARTOOLKIT_CONFIG'] = conf

        library_location = os.path.abspath(os.path.join(os.path.dirname(__file__), 'patterns/libPatterns.so'))
        self.multiPatternLib = cdll.LoadLibrary(library_location)

        self.data_params = os.path.abspath(os.path.join(os.path.dirname(__file__), 'patterns/Data'))

        self.exit_th = False
        #self.lock_data = threading.Lock()

        #self.multiPatternLib.arMultiMarkerTrigDist.restype =c_double
        #Export the ARTOOLKIT_CONFIG system variable which will be used by artoolkit

    def iter_run(self):
        while not self.exit_th:
            #self.lock_data.acquire()
            self.multiPatternLib.arMultiRefresh()
            #self.lock_data.release()
            #print "corriendo trread" + str(i)
            time.sleep(self.refresh_delay)
        self.multiPatternLib.arMultiCleanup()
        #print "SALIMOS WHILE"

    def init(self):
        self.multiPatternLib.arMultiInit(self.data_params)
        self.exit_th = False
        t = threading.Thread(target=self.iter_run)
        t.start()

    def refresh(self):
        self.multiPatternLib.arMultiRefresh()

    def cleanup(self):
        self.exit_th = True

    def isMarkerPresent(self, marker):
        #self.lock_data.acquire()
        ret = self.multiPatternLib.arMultiIsMarkerPresent(marker)
        #self.lock_data.release()
        return ret

    def getMarkerTrigDist(self, marker):
        #self.lock_data.acquire()
        ret = self.multiPatternLib.arMultiMarkerTrigDist(marker)
        #self.lock_data.release()
        return ret

    def arMultiGetIdsMarker(self):
        s = create_string_buffer('\000'*256*self.OBJECT_MAX)
        ok = self.multiPatternLib.arMultiGetIdsMarker(self.data_params, s)
        if ok:
            return  s.value
        else:
            return ""

