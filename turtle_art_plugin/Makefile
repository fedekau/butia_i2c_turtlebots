# Makefile for butia
#
# Copyright (C) 2008 Guillermo Reisch (greisch@fing.edu.uy)
# Copyright (C) 2010 Andres Aguirre (aaguirre@fing.edu.uy)
#
# Butia is a free open plataform for robotics projects
# http://www.fing.edu.uy/inco/proyectos/butia
# Universidad de la República del Uruguay
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


#versions to checkout before build
TURTLEBLOCKS_VERSION = 1e74d47a4f233dc72e7c9698b1ab3ed66d4d19fc
EXTRAS_VERSION = bf7c5b26f24205548e28b95572305d7df43e4f62
NXT_VERSION = a0c2ed0f2681a218a435dfa178cd69dafabb3e8c
WEDO_VERSION = 67e4233bc4944253ca75de204c158bd36cafd997


SHELL = /bin/sh
# check work in "sh" instad of bash, make it more portable!!!
INSTALL = install
INSTALL_PROGRAM = $(INSTALL)
INSTALL_DATA = ${INSTALL} -m 644
LESS = less
BUILDDIR = tmp
NOGIT =

#intallation directorys
prefix = /usr/local
exec_prefix = $(prefix)
bindir = $(exec_prefix)/bin
sbindir = $(exec_prefix)/sbin
libexecdir = $(exec_prefix)/libexec
datarootdir = $(prefix)/share
datadir = $(datarootdir)
sysconfdir = $(prefix)/etc
sharedstatedir = $(prefix)/com
localstatedir = $(prefix)/var
includedir = $(prefix)/include
oldincludedir = $(prefix)/include
docdir = $(datarootdir)/doc/tortubots
infodir = $(datarootdir)/info
libdir = $(exec_prefix)/lib
localedir = $(datarootdir)/locale
mandir = $(datarootdir)/man
man1dir = $(mandir)/man1
man2dir = $(mandir)/man2 # etc... etc...
activitiesdir = $(datadir)/sugar/activities



all: apply_hard_plugins


help:
	if [ -e /usr/bin/less ] ; then $(LESS) INSTALL ; fi
	# if the user not have less command...
	cat INSTALL

############# init of submodules #################

first:
	(cd .. && git submodule update --init)

############# initialization of "especific" submodules ###############

mainline/.git:
	$(MAKE) first

WeDoMore/.git:
	$(MAKE) first

turtle-extras/.git:
	$(MAKE) first

nxt_plugin/.git:
	$(MAKE) first

############# checkout a version of submodule ##################
SUBMODULE = mainline
SUBMODULEVER = master

checkoutsm:
ifndef NOGIT
	(cd $(SUBMODULE) && git clean -xdf ) 
	(cd $(SUBMODULE) && if (git checkout $(SUBMODULEVER) ); then echo OK ; else git fetch ; git checkout $(SUBMODULEVER) ; fi )
endif

############# checkout a especific version of submodules ##############

walterGIT: mainline/.git
	$(MAKE) SUBMODULE=mainline SUBMODULEVER=$(TURTLEBLOCKS_VERSION) checkoutsm

extrasGIT: turtle-extras/.git
	$(MAKE) SUBMODULE=turtle-extras SUBMODULEVER=$(EXTRAS_VERSION) checkoutsm

wedoGIT: WeDoMore/.git
	$(MAKE) SUBMODULE=WeDoMore SUBMODULEVER=$(WEDO_VERSION) checkoutsm

nxtGIT: nxt_plugin/.git
	$(MAKE) SUBMODULE=nxt_plugin SUBMODULEVER=$(NXT_VERSION) checkoutsm


################ Support for lua (bobot-server) ######################

butiaXO:
	# I want butiaXO folder be OK! (needed by plugin)
	make -C ../butiaXO


################ Construction...

mktmpfolder:
	#making folders and copying mainline
	rm -rf $(BUILDDIR)
	cp -rL mainline $(BUILDDIR)
	rm -rf $(BUILDDIR)/.git
	rm -f  $(BUILDDIR)/.gitignore
	# lets patch the activity.info and add some icons (TurtleBlocks => TurtleBots)
	cp -rLf stagin/activity $(BUILDDIR)/

apply_localization: walterGIT mktmpfolder extrasGIT
	# let's add localization (if is not already in taextras.py)
	(cd turtle-extras && ./merge.py turtlebots)
	cp turtle-extras/taextras.py $(BUILDDIR)
	# fix localization (compile .po)
	(cd $(BUILDDIR) && python setup.py build)
	#msgcat butia/po/es.po tmp/po/es.po -o tmp/po/es.po
	#msgcat sumtia/po/es.po tmp/po/es.po -o tmp/po/es.po
	#msgcat followme/po/es.po tmp/po/es.po -o tmp/po/es.po
	#msgcat nxt_plugin/po/es.po tmp/po/es.po -o tmp/po/es.po

apply_hard_plugins: apply_localization butiaXO walterGIT nxtGIT wedoGIT
	cp -rLf butia         $(BUILDDIR)/plugins/
	cp -rLf sumtia        $(BUILDDIR)/plugins/
	cp -rLf followme/     $(BUILDDIR)/plugins/
	cp -rLf nxt_plugin/   $(BUILDDIR)/plugins/
	cp -rLf wedo_plugin/  $(BUILDDIR)/plugins/

apply_sym_plugins: walterGIT nxtGIT wedoGIT apply_localization butiaXO
	# let's make symlinks, it lets you, edit and try, more easily!
	ln -s `pwd`/butia         $(BUILDDIR)/plugins/butia
	ln -s `pwd`/sumtia        $(BUILDDIR)/plugins/sumtia
	ln -s `pwd`/followme      $(BUILDDIR)/plugins/followme
	ln -s `pwd`/nxt_plugin    $(BUILDDIR)/plugins/nxt_plugin
	ln -s `pwd`/wedo_plugin   $(BUILDDIR)/plugins/wedo_plugin

xo: apply_hard_plugins
	# remove .git from NXT plugin
	rm -rf $(BUILDDIR)/plugins/nxt_plugin/.git
	rm -f $(BUILDDIR)/plugins/nxt_plugin/.gitignore
	# ok, let's make this .xo
	(cd $(BUILDDIR) && python setup.py build)
	#dist_xo no work in the tmp folder
	(cd $(BUILDDIR) && python setup.py dist_xo)
	cp $(BUILDDIR)/dist/*.xo .
	#$(MAKE) clean_tmp

dev: apply_sym_plugins
	rm -rf ~/Activities/TurtleBots.activity
	mkdir -p ~/Activities
	(cd $(BUILDDIR) && python setup.py dev)


################ Plugins #############

plugin-butia: apply_hard_plugins
	cp stagin/plugins/butia/plugin.info $(BUILDDIR)/plugins
	(cd $(BUILDDIR)/plugins && tar -czvf butia_plugin.tar.gz butia/* plugin.info)
	rm $(BUILDDIR)/plugins/plugin.info
	mv $(BUILDDIR)/plugins/butia_plugin.tar.gz .

plugin-followme: apply_hard_plugins
	cp stagin/plugins/followme/plugin.info $(BUILDDIR)/plugins
	(cd $(BUILDDIR)/plugins && tar -czvf followme_plugin.tar.gz followme/* plugin.info)
	rm $(BUILDDIR)/plugins/plugin.info
	mv $(BUILDDIR)/plugins/followme_plugin.tar.gz .

plugin-nxt: apply_hard_plugins
	# remove .git from NXT plugin
	rm -rf $(BUILDDIR)/plugins/nxt_plugin/.git
	rm -f $(BUILDDIR)/plugins/nxt_plugin/.gitignore
	cp stagin/plugins/nxt_plugin/plugin.info $(BUILDDIR)/plugins
	cd $(BUILDDIR)/plugins && tar -czvf nxt_plugin.tar.gz nxt_plugin/* plugin.info
	rm $(BUILDDIR)/plugins/plugin.info
	mv $(BUILDDIR)/plugins/nxt_plugin.tar.gz .

plugin-wedo: apply_hard_plugins
	cp stagin/plugins/wedo_plugin/plugin.info $(BUILDDIR)/plugins
	cd $(BUILDDIR)/plugins && tar -czvf wedo_plugin.tar.gz wedo_plugin/* plugin.info
	rm $(BUILDDIR)/plugins/plugin.info
	mv $(BUILDDIR)/plugins/wedo_plugin.tar.gz .

plugins: plugin-butia plugin-followme plugin-nxt plugin-wedo

plugin-all: plugins

############### Install procedures #################

install-activity: xo
	sugar-install-bundle *.xo

install-xo: install-activity

install: all install-permissions
	$(MAKE) prefix= install-rules
	echo "Instaling..."
	mkdir -p $(DESTDIR)$(activitiesdir)
	cp -r $(BUILDDIR) $(DESTDIR)$(activitiesdir)/TurtleBots.activity
	#mv $(DESTDIR)/usr/share/sugar/activities/tmp $(DESTDIR)/usr/share/sugar/activities/TurtleBots.activity
	#cp IconosTortuBots.desktop ~/.local/share/applications/ 1>>"$ARCHIVO_LOG" 2>>"$ARCHIVO_LOG"

install-permissions:
	if [ -e $(DESTDIR)/etc/group ] ; then \
          addgroup --system lego ; \
          ./permissions.sh ; \
        fi ;


install-strip: install
	#strip $(DESTDIR) file...

install-rules:
	mkdir -p $(DESTDIR)$(sysconfdir)/udev/rules.d
	$(INSTALL_DATA) rules/70-lego.rules $(DESTDIR)$(sysconfdir)/udev/rules.d
	$(INSTALL_DATA) rules/99-usb4all.rules $(DESTDIR)$(sysconfdir)/udev/rules.d


############### UNInstall procedures #################

uninstall-activity:
	rm -rf ~/Activities/TurtleBots.activity

uninstall-xo: uninstall-activity

uninstall-dev: uninstall-activity

uninstall-strip: uninstall
	#unstrip $(DESTDIR) file... :-P

uninstall:
	$(MAKE) prefix= uninstall-rules
	#this should by change to rmdir -p --ignore-fail-on-non-empty
	rm -rf ~/Activities/TurtleBots.activity
	rm -rf $(DESTDIR)$(activitiesdir)/TurtleBots.activity
	rm -rf $(DESTDIR)$(localedir)/es/LC_MESSAGES/org.laptop.TurtleArtButia.mo

uninstall-permissions:
	if [ -e $(DESTDIR)/etc/group ] ; then \
          # remove group (actuali I dont knock how to remove group winout error if not exist) \
          if (delgroup --system lego) ; then echo group removed... ; fi ; \
        fi ;

uninstall-rules:
	rm -f $(DESTDIR)$(sysconfdir)/udev/rules.d/70-lego.rules
	rm -f $(DESTDIR)$(sysconfdir)/udev/rules.d/99-usb4all.rules
	rmdir -p --ignore-fail-on-non-empty $(DESTDIR)$(sysconfdir)/udev/rules.d


####### CLEAN STUFF ######


clean: clean-tmp clean-plugins clean-xo clean-builddir
	$(MAKE) -C ../butiaXO clean
	# this remove only if it's a symlink ; don't remove if installed
	rm -f ~/Activities/TurtleBots.activity

clean-tmp:
	rm -rf tmp

clean-builddir:
	rm -rf $(BUILDDIR)

clean-xo:
	rm -f *.xo

clean-plugins:
	rm -f *.tar.gz


.SUFFIXES:
.SUFFIXES: .c .o .py .pyc .po .pot

# targets that not represent generated files
.PHONY: all help \
 clean clean-tmp clean-builddir clean-xo clean-plugins \
 first walterGIT extrasGIT wedoGIT nxtGIT \
 butiaXO mktmpfolder apply_hard_plugins apply_sym_plugins \
 genpot genpot_notraslated updatepo xo \
 install install-strip \
 uninstall uninstall-strip \
 plugin-butia plugin-followme plugin-nxt plugin-wedo plugins plugin-all \
 dev
