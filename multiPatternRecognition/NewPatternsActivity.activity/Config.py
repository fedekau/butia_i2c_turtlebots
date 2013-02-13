#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ConfigParser
import string
from jarabe.model import bundleregistry
from gettext import gettext as _
import os

class Config:
    __TurtleArt =None
    __plugin_folder=None
    def __init__(self,fileConf = "properties.conf"):
        print fileConf
        #chequear que exista el archivo y corte
        if not os.path.exists(fileConf):
             raise Exception(_("No se encuentra el archivo de configuración"))
         
        config = ConfigParser.ConfigParser()
        config.read(fileConf)
        for opt in config.options("TurtleArtEnabled"):
            aux_sec = config.get("TurtleArtEnabled",opt)
            if self.__is_turtle_installed(aux_sec):
                self.__TurtleArt = aux_sec
                break

        if  self.__TurtleArt is None:
            #ver de dar un error o tirar una excepcion
            raise Exception(_("No esta instalado TortuBots o compatible"))
        
        self.__gen_turtle_path(self.__TurtleArt,config.get("PluginFolder","folder"))
         

    def __gen_turtle_path(self,turtle_id,plugin_folder):
        #genero el path al plugin
        #turtle_path ="algo"
        print "turtle id:" , turtle_id
        turtle_path = bundleregistry.get_registry().get_bundle(turtle_id).get_path()
        self.__plugin_folder = turtle_path + "/plugins/" + plugin_folder


        
    def __is_turtle_installed(self,turtle_id):
          #reviso que exista el torutga para ese id
          bunlde = None
          bunlde = bundleregistry.get_registry().get_bundle(turtle_id)
          if (bunlde is None):
              return False
          else:
              return True

    def is_plugin_installed(self):
        return os.path.isdir(self.__plugin_folder)
    
    def get_plugin_folder(self):
        return self.__plugin_folder
    
    def get_TurleArt_Id(self):
        return self.__TurtleArt

    def get_plugin_image_path(self):
        return self.get_plugin_folder() + "/images"

    def get_plugin_library_path(self):
        return self.get_plugin_folder() + "/library"

    def get_plugin_data_path(self):
        return self.get_plugin_library_path() + "/multiPatternDetection/Data"

