#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Pango is a library for rendering internationalized texts


import gtk
import gtk.glade
from gettext import gettext as _
from jarabe.model import bundleregistry
import sys,os
import shutil

import pygtk
pygtk.require("2.0")
import gtk

from pysvg.structure import *
from pysvg.core import *
from pysvg.text import *
from pysvg import parser
from config import *

#plugin_name = 'pattern'
#plugin_folder = 'pattern_detection'

#turtlepath = bundleregistry.get_registry().get_bundle('org.laptop.TurtleArtButia').get_path()
try:
    conf = Config("./properties.conf")
    sys.path.insert(0,conf.get_plugin_library_path())
    if conf.is_plugin_installed():
        import multiPatternDetectionAPI as detectionAPI
except Exception as inst:
#    md = gtk.MessageDialog(None,
#    gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR,
#    gtk.BUTTONS_CLOSE, _("Atención, problemas al abrir el archivo de configuración:")+ str(e))
#    md.run()
#    md.destroy()
    print _("ActivityWindows - Error inesperado:")
    print type(inst)     # la instancia de excepción
    print inst.args      # argumentos guardados en .args
    print inst           # __str__ permite imprimir args directamente
    #gtk.main_quit()
    raise inst



class ActivityWindows:
    detection = None
    conf = None
    model_TV = None
    col_TV = None

    def __init__(self, runaslib=True):
        # Load Glade XML
        self.xml = gtk.glade.XML("NewPatterns.glade")
        # get Library
        self.detection = detectionAPI.detection()
        self.conf = Config("./properties.conf")
        # Get Window
        self.w = self.xml.get_widget('window1')
        self.on_load_translate()
        self.w.connect("delete_event", gtk.main_quit)

        # Get Windows child
        self.w_child = self.w.get_child()
        # self.widget will be attached to the Activity
        # This can be any GTK widget except a window
        self.widget = self.w_child

        if not runaslib:
            self.w.show_all()
            gtk.main()

    def on_load_translate(self):
        #TAB 1
        label = self.xml.get_widget('lblStep1')
        label.set_label(_("Marcas del Sistema"))

        treeMarcas = self.xml.get_widget('treeMarcas')
        self.add_lista_marcas(treeMarcas)

        btn = self.xml.get_widget('btnBorrar')
        btn.set_label(_("Eliminar marca"))
        btn.connect('clicked', self.on_btn_delete)
        btn.hide()

        #TAB 2
        label = self.xml.get_widget('lblStep2')
        label.set_text(_("Agregar Marcas"))

        label = self.xml.get_widget('label5')
        label.set_text(_("Identificador (sin espacios)"))

        label = self.xml.get_widget('label4')
        label.set_text(_("Seleccionar archivo .patt"))

        label = self.xml.get_widget('label6')
        label.set_text(_("Seleccionar Icono SVG(opcional)"))

        label = self.xml.get_widget('lblSize')
        label.set_text(_("Tamaño (mm)"))

        btn = self.xml.get_widget('btn_open_patt')
        btn.set_label(_("Buscar Patt"))
        btn.connect('clicked', self.file_Open_Patt)

        btn = self.xml.get_widget('btn_icono')
        btn.set_label(_("Buscar Icono"))
        btn.connect('clicked', self.file_Open_Icon)

        btn = self.xml.get_widget('btn_Acept')
        btn.set_label(_("Aceptar"))
        btn.connect('clicked', self.on_btn_accept)

        btn = self.xml.get_widget('btn_clean')
        btn.set_label(_("Limpiar Icono"))
        btn.connect('clicked', self.clean_icon)
        btn.hide()

        txtInp = self.xml.get_widget('txtSize')
        txtInp.set_text('160')

        lnk = self.xml.get_widget('lnkWiki')
        lnk.set_label(_('¿Como obtener los archivos .patt?'))
        lnk.set_uri(_("http://www.fing.edu.uy/inco/proyectos/butia/mediawiki/index.php/Butia_reconocimiento_marcas"))

        #TAB 3
        #label = self.xml.get_widget('lblStep3')
        #label.set_text(_("Quitar Marca"))
        #view = self.xml.get_widget('iconview1')
        #self._on_load_icons(view)


    def add_lista_marcas(self,treeView):
        if self.model_TV is not None:
            self.model_TV.clear()

        lista = None
        lista = gtk.ListStore(str)
        marcas = self.detection.arMultiGetIdsMarker().split(';')
        for m in marcas:
            lista.append([m])

        self.model_TV = lista
        treeView.set_model(self.model_TV)

        #First column's cell
        cell = gtk.CellRendererText()
        if self.col_TV is None:
            self.col_TV = gtk.TreeViewColumn(_("Marcas actuales"))
            self.col_TV.pack_start(cell, True)
            self.col_TV.set_attributes(cell,text=0, foreground=2, background=3)
            treeView.append_column(self.col_TV)

        treeselection = treeView.get_selection()
        treeselection.set_mode(gtk.SELECTION_SINGLE)
        treeselection.set_select_function(self.on_select_list,self.model_TV, True)

        #treeView.set_cursor(data[0])

    def on_select_list(self, selection, model, path, is_selected, user_data):
        iter = model.get_iter(path)
        directorio =  model.get_value(iter, 0)

        actBot = None
        actBot = bundleregistry.get_registry().get_bundle('org.laptop.TurtleArtButia')
        fname = actBot.get_path() + "/plugins/pattern_detection/images/"+directorio+"off.svg"
        if not os.path.exists(fname):
            fname = "./images/noicon.svg"
        image = self.xml.get_widget('imgIcono')
        pixbuf = gtk.gdk.pixbuf_new_from_file(fname)
        scaled_buf = pixbuf.scale_simple(140,140,gtk.gdk.INTERP_BILINEAR)
        image.set_from_pixbuf(scaled_buf)
        image.show()
        btn = self.xml.get_widget('btnBorrar')
        btn.show()
        return True

    def on_btn_delete(self, *args):
        treeMarcas = self.xml.get_widget('treeMarcas')
        entry1, entry2 = treeMarcas.get_selection().get_selected()
        entry = entry1.get_value(entry2, 0)
        md = gtk.MessageDialog(None,
        gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_QUESTION,
        gtk.BUTTONS_YES_NO, _("Atención, Estas seguro que deseas eliminar la marca: ") + entry)
        response = md.run()
        md.destroy()
        if response == gtk.RESPONSE_NO:
            return
        #Elimino la marca de object_data
        if not self.delete_from_object_data(entry):
            return

        #Elimino el patt
        #os.path.abspath(turtlepath + '/plugins/'+plugin_folder+'/library/multiPatternDetection/Data')
        datapath =  self.conf.get_plugin_data_path()


        file = entry.lower() + ".patt"
        os.remove(datapath+"/"+file)

        #Elimino los svg si tiene
        #os.path.abspath(turtlepath + '/plugins/'+plugin_folder+'/images')
        imageFolder = self.conf.get_plugin_image_path()
        if os.path.exists(imageFolder + "/" + entry + "off.svg"):
            os.remove(imageFolder + "/" + entry + "off.svg")
            os.remove(imageFolder + "/" + entry + "small.svg")

        self.tree_refresh()

    def delete_from_object_data(self,idMarca):
        lines = []
        datapath =  self.conf.get_plugin_data_path()
        f= open(datapath + "/object_data", "r")
        lines = f.readlines()
        f.close()
        iMarca=0
        #idMarca =entry
        try:
            iMarca= lines.index(idMarca+"\n")
            print iMarca

            i= lines.index("#number of patterns\n")

            #modifico la cantidad de marcas
            cant = int(lines[i+1]) - 1
            lines[i+1]=str(cant)+"\n"
            # quito desde la linea del comentario
            # hasta el salto de linea de separacion con la siguiente marca
            del lines[iMarca-2:iMarca+4]

            #escribo el archivo
            f = open(datapath + "/object_data", "w")
            f.writelines(lines)
            f.close()

        except Exception, err:
           md = gtk.MessageDialog(None,
           gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR,
           gtk.BUTTONS_CLOSE, _("Atención, problemas al abrir el archivo de marcas") + err)
           md.run()
           md.destroy()
           return False

        return True

    def on_btn_accept(self, *args):

        idMark = None
        idMark = self.xml.get_widget('txtID').get_text()
        if idMark is None or idMark == '':
            md = gtk.MessageDialog(None,
            gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR,
            gtk.BUTTONS_CLOSE, _("Atención, debe selecionar un identificador de marcas"))
            md.run()
            md.destroy()
            return

        if ' ' in idMark:
            md = gtk.MessageDialog(None,
            gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR,
            gtk.BUTTONS_CLOSE, _("Atención, el identificador no puede tener espacios"))
            md.run()
            md.destroy()
            return

        txtFilePatt = None
        txtFilePatt = self.xml.get_widget('txtPatt').get_text()
        if txtFilePatt is None or txtFilePatt == '':
            md = gtk.MessageDialog(None,
            gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR,
            gtk.BUTTONS_CLOSE, _("Atención, debes de selcionar un archivo .patt"))
            md.run()
            md.destroy()
            return

        txtSize = None
        txtSize = self.xml.get_widget('txtSize').get_text()
        if txtSize is None or txtSize == '':
            md = gtk.MessageDialog(None,
            gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR,
            gtk.BUTTONS_CLOSE, _("Atención, debes seleccionar un tamaño de marca valido"))
            md.run()
            md.destroy()
            return

        #Pongo en mayusculas la primer letra
        idMark = idMark.capitalize()

        #chequeco que si existe el id, se quiera sobreescribir
        marcas = self.detection.arMultiGetIdsMarker()

        if idMark in marcas:
            md = gtk.MessageDialog(None,
            gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_QUESTION,
            gtk.BUTTONS_YES_NO, _("Atención, ya tienes una marca con ese identificador, ¿deseas sobreescribirla?"))
            response = md.run()
            md.destroy()
            if response == gtk.RESPONSE_NO:
                return
            else:#tengo que eliminar la marca del object_data
                self.delete_from_object_data(idMark)

        # modifico el object_data
        lines = []
        try:
            #os.path.abspath(turtlepath + '/plugins/'+plugin_folder+'/library/multiPatternDetection/Data')
            datapath = datapath =  self.conf.get_plugin_data_path()
            f= open(datapath + "/object_data", "r")
            lines = f.readlines()
            f.close()
        except:
            md = gtk.MessageDialog(None,
            gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR,
            gtk.BUTTONS_CLOSE, _("Atención, problemas al abrir el archivo de marcas"))
            md.run()
            md.destroy()
            return
        i=0
        try:
            i = lines.index("#number of patterns\n")
            cant = int(lines[i+1]) + 1

            lines[i+1]=str(cant)+"\n"
            f = open(datapath + "/object_data", "w")

            coment="patter " + idMark
            idMarca=idMark
            patt =idMark.lower() + ".patt"
            size = txtSize
            center ="0,0 0,0"

            lines.append("\n" )
            lines.append("# " + coment+"\n")
            lines.append(idMarca+"\n")
            lines.append(patt+"\n")
            lines.append(size +"\n")
            lines.append(center+"\n")
            f.writelines(lines)
            f.close()
        except Exception, err:
            md = gtk.MessageDialog(None,
            gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR,
            gtk.BUTTONS_CLOSE, _("Atención, problemas al actualizar el archivo de marcas") + err)
            md.run()
            md.destroy()
            return
        #copio archivos
        copyFile = datapath + "/" + patt
        shutil.copy(txtFilePatt, copyFile)
        txtIco = None
        txtIco = self.xml.get_widget('txtIcon').get_text()
        if not (txtIco == ''):
            self.copy_Icons(txtIco, idMark)
        md = gtk.MessageDialog(None,
        gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_INFO,
        gtk.BUTTONS_CLOSE, _("Marca agregada satisfactoriamente!"))
        md.run()
        md.destroy()
        self.clean_all()

    def clean_all (self):
        self.clean_icon("")
        self.xml.get_widget('txtSize').set_text('160')
        self.xml.get_widget('txtID').set_text('')
        self.xml.get_widget('txtPatt').set_text('')
        self.tree_refresh()

    def tree_refresh(self):
        treeMarcas = self.xml.get_widget('treeMarcas')
        self.add_lista_marcas(treeMarcas)

    def on_btn_accept_test(self, *args):
        idMark = "PP"
        txtIco = None
        txtIco = self.xml.get_widget('txtIcon').get_text()
        self.copy_Icons(txtIco, idMark)


    def copy_Icons(self,iconOrig,idMark):
        imageFolder =  self.conf.get_plugin_image_path() #os.path.abspath(turtlepath + '/plugins/'+plugin_folder+'/images')
        self.make_icons(iconOrig, 70,  imageFolder + "/" + idMark + "off.svg")
        self.make_icons(iconOrig, 40,  imageFolder + "/" + idMark + "small.svg")

    def make_icons(self,iconSRC,size,iconDest):
        original = parser.parse(iconSRC)
        #print  original.get_height()
        #print  original.get_width()
        fw = size / float(original.get_width())
        fh = size / float(original.get_height())
        original.set_width(size)
        original.set_height(size)
        original.set_transform("translate(0, 0) scale(" + str(fw)+"," + str(fh)+")")
        original.save(iconDest)
        #dest=svg(width=str(size)+"px", height=str(size)+"px")
        #dest.addElement(original)
        #dest.save(iconDest)

    def _on_load_icons(self,view):
        model = gtk.ListStore(str, gtk.gdk.Pixbuf)
        view.set_model(model)
        view.set_text_column(0)
        view.set_pixbuf_column(1)
        view.set_columns(4)
        #obtengo la direccion del tortubots
        #actBot = None
        #actBot = bundleregistry.get_registry().get_bundle('org.laptop.TurtleArtButia')
        #if actBot is not None:
        imgFolder = self.conf.get_plugin_image_path()
        files = os.listdir(imgFolder)
        for image in files:
            pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(imgFolder+"/%s" %image, 72, 72)
            model.append([image, pixbuf])
            model.append([image, pixbuf])
        view.set_selection_mode(gtk.SELECTION_SINGLE)
        view.connect('selection-changed', self.on_select, model)

    def on_select(self, icon_view, model=None):
        selected = icon_view.get_selected_items()
        if len(selected) == 0: return
        i = selected[0][0]
        category = model[i][0]
        if self.current_frame is not None:
            self.content_box.remove(self.current_frame)
            self.current_frame.destroy()
            self.current_frame = None

        self.current_frame = gtk.Frame('General')
        self.content_box.pack_end(self.current_frame, fill=True, expand=True)
        self.show_all()


    def clean_icon(self, *args):
        txtFileName = self.xml.get_widget('txtIcon')
        txtFileName.set_text('')
        image = self.xml.get_widget('imgIco')
        image.set_property('visible', False)
        btn = self.xml.get_widget('btn_clean')
        btn.set_property('visible', False)

    def file_Open_Patt(self, *args):
        filter = gtk.FileFilter()
        filter.set_name(_("Archivos .patt"))
        filter.add_pattern("*.patt")
        fname=self._filechosser(_("Cargando archivos .patt"), filter)
        if fname != None:
            txtFileName = self.xml.get_widget('txtPatt')
            txtFileName.set_text(fname)

    def file_Open_Icon(self, *args):
        filter = gtk.FileFilter()
        filter.set_name(_("Archivos .svg"))
        filter.add_pattern("*.svg")
        fname=self._filechosser(_("Cargando archivos .svg"), filter)
        if fname != None:
            txtFileName = self.xml.get_widget('txtIcon')
            txtFileName.set_text(fname)
            image = self.xml.get_widget('imgIco')
            pixbuf = gtk.gdk.pixbuf_new_from_file(fname)
            scaled_buf = pixbuf.scale_simple(72,72,gtk.gdk.INTERP_BILINEAR)
            image.set_from_pixbuf(scaled_buf)
            image.show()
            btn = self.xml.get_widget('btn_clean')
            btn.show()

    def _filechosser(self, ventana_titulo,filter):
        dialog = gtk.FileChooserDialog(ventana_titulo, None, \
              gtk.FILE_CHOOSER_ACTION_OPEN, \
             (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        dialog.set_default_response(gtk.RESPONSE_OK)

        dialog.add_filter(filter)
        fname = None
        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            fname = dialog.get_filename()
        dialog.destroy()
        return fname


    def on_btn_hello(self, *args):
        md = gtk.MessageDialog(None,
        gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_QUESTION,
        gtk.BUTTONS_OK_CANCEL, "Are you sure to quit?")
        md.run()
        md.destroy()

    def on_btn_quit(self, *args):
        gtk.main_quit()


if __name__ == '__main__':
    ActivityWindows(False)
