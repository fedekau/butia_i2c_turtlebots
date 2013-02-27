from ctypes import *
import platform

import os
import time
#Library: multiPatternDetectionAPI

#>>> from ctypes import *
#>>> multiPatternLib = cdll.LoadLibrary('./libMultiPatternDetection.so')
#>>> multiPatternLib.arMultiInit()
import threading


class detection:
    multiPatternLib = None
    video = None
    OBJECT_MAX = 30
    exit_th = False
    lock_exit = None
    lock_data = None
    refresh_delay = 0.1

    #Init de la clase robot
    def __init__(self, video = "/dev/video0" ):
        self.video = video
        os.environ['ARTOOLKIT_CONFIG']= 'v4l2src device='+self.video+' use-fixed-fps=false ! ffmpegcolorspace ! capsfilter caps=video/x-raw-rgb,bpp=24 ! identity name=artoolkit ! fakesink'

        #Load the libglu.so.3, or else ctypes won't find it if it's not installed in the system
        arq,so = platform.architecture()
        if arq == '32bit':
            glut_location = os.path.abspath(os.path.join(os.path.dirname(__file__), 'lib/32bits/libglut.so.3'))
        else:
            glut_location = os.path.abspath(os.path.join(os.path.dirname(__file__), 'lib/64bits/libglut.so.3'))

        cdll.LoadLibrary(glut_location)

        library_location = os.path.abspath(os.path.join(os.path.dirname(__file__), 'multiPatternDetection/libMultiPatternDetection.so'))
        self.multiPatternLib = cdll.LoadLibrary(library_location)


        self.exit_th = False
        self.lock_exit = threading.Lock()
        self.lock_data = threading.Lock()
        #self.multiPatternLib.arMultiMarkerTrigDist.restype =c_double

        #Export the ARTOOLKIT_CONFIG system variable which will be used by artoolkit

    def iter_run(self):
          #i = 0
          while not self.exit_th:
              #i=i+1
              #self.lock_data.acquire()
              self.multiPatternLib.arMultiRefresh()
              #self.lock_data.release()
              #print "corriendo trread" + str(i)
              time.sleep(self.refresh_delay)
          self.multiPatternLib.arMultiCleanup()
          #print "SALIMOS WHILE"

    def init(self):
        data_params = os.path.abspath(os.path.join(os.path.dirname(__file__), 'multiPatternDetection/Data'))
        self.multiPatternLib.arMultiInit(data_params)
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
          data_params = os.path.abspath(os.path.join(os.path.dirname(__file__), 'multiPatternDetection/Data'))
          s = create_string_buffer('\000'*256*self.OBJECT_MAX)

          ok = self.multiPatternLib.arMultiGetIdsMarker(data_params,s)
          if ok:
              return  s.value
          else:
              return ""



