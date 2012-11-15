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
#

TURTLEBLOCKS_VERSION = 3d80bec755ef4c807197592949602d24f774cd8d
EXTRAS_VERSION = bf7c5b26f24205548e28b95572305d7df43e4f62
NXT_VERSION = a0c2ed0f2681a218a435dfa178cd69dafabb3e8c
WEDO_VERSION = 67e4233bc4944253ca75de204c158bd36cafd997


CWD = $(cwd)
SHELL = /bin/sh
# check work in "sh" instad of bash, make it more portable!!!
INSTALL = install
INSTALL_PROGRAM = $(INSTALL)
INSTALL_DATA = ${INSTALL} -m 644



all: help


help:
	@echo 
	@echo " This is a Makefile for compile/construct TurtleArtButia.        "
	@echo " The follow objetives are defined:                               "
	@echo "    first: Execute this command to init the submodules only the  "
	@echo "          first time after clone                                 "
	@echo "    xo : Generate the XO distribuible package                    "
	@echo "    dev: compile all necessary for TurtleArtButia                "
	@echo "                 and make a developed sugar install              "
	@echo "                 this allow to work and easy change the code     "
	@echo "    install: install activity                                    "
	@echo "    uninstall: unistall activity                                 "
	@echo "    clean: clean all compiled/generated files                    "
	@echo "    genpot: generate pot of plugings                             "
	@echo "    genpot_notraslated: generate pot the plugings that are       "
	@echo "                        not already traslated in taextras.py     "
	@echo "    updatepo: using notraslated.pot update the es.po of plugin's "
	@echo "              the other traslations all already set in mainline  "
	@echo "              of Walter, so use that traslations.                "
	@echo "                                                                 "
	@echo " The follow parameters are optional:                             "
	@echo "    TURTLEBLOCKS_VERSION=[version or commit]                     "
	@echo "                         (default $(TURTLEBLOCKS_VERSION))       "
	@echo "                                                                 "
	@echo "           For more info contact \"butia@fing.edu.uy\"           "
	@echo "   wiki: http://www.fing.edu.uy/inco/proyectos/butia/mediawiki   "
	@echo "                                                                 "    



############# init of submodules #################

first:
	(cd .. && git submodule update --init --merge)

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
	(cd $(SUBMODULE) && git clean -xdf)
	(cd $(SUBMODULE) && if (git checkout $(SUBMODULEVER) ); then echo OK ; else git fetch ; checkout $(SUBMODULEVER) ; fi )


############# checkout a especific version of submodules ##############

walterGIT: mainline/.git
	$(MAKE) SUBMODULE=mainline SUBMODULEVER=$(TURTLEBLOCKS_VERSION) checkoutsm

extrasGIT: turtle-extras/.git
	$(MAKE) SUBMODULE=turtle-extras SUBMODULEVER=$(EXTRAS_VERSION) checkoutsm

wedoGIT: WeDoMore/.git
	$(MAKE) SUBMODULE=WeDoMore SUBMODULEVER=$(WEDO_VERSION) checkoutsm

nxtGIT: nxt_plugin/.git
	$(MAKE) SUBMODULE=nxt_plugin SUBMODULEVER=$(NXT_VERSION) checkoutsm

#####################   DEPRECATED!!!!! ##############################
########### POT GENERATION AND TRASLATION THINKS #####################
####
####POT_FILES= butia/po/Butia.pot sumtia/po/Sumtia.pot followme/po/FollowMe.pot
####POT_PROP= --language=Python --add-comments=TRANS: --keyword=_ --join-existing
####
####POT_NT_FILES= butia/po/Butia.notraslated.pot sumtia/po/Sumtia.notraslated.pot \
####              followme/po/FollowMe.notraslated.pot
####
####PO_FILES= butia/po/es.po sumtia/po/es.po followme/po/es.po nxt_plugin/po/es.po
####
####
###### Generate pot of plugins
####genpot: $(POT_FILES)
####
####butia/po/Butia.pot: butia/butia.py
####	echo msgid \"\" > $@
####	echo msgstr \"\" >> $@
####	echo \"Content-Type: text/plain\; charset=UTF-8\" >> $@
####	xgettext $(POT_PROP) $< -o $@
####
####sumtia/po/Sumtia.pot: sumtia/sumtia.py
####	echo msgid \"\" > $@
####	echo msgstr \"\" >> $@
####	echo \"Content-Type: text/plain\; charset=UTF-8\" >> $@
####	xgettext $(POT_PROP) $< -o $@
####
####followme/po/FollowMe.pot: followme/followme.py
####	echo msgid \"\" > $@
####	echo msgstr \"\" >> $@
####	echo \"Content-Type: text/plain\; charset=UTF-8\" >> $@
####	xgettext $(POT_PROP) $< -o $@
####
####
###### Generate a pot of MSGID that ARE NOT ALREADY translated in mainline (Walter GIT)
####genpot_notraslated: $(POT_NT_FILES)
####
####butia/po/Butia.notraslated.pot: butia/po/Butia.pot 
####	msgmerge --no-fuzzy-matching mainline/po/es.po $< | msgattrib --no-obsolete --untranslated > $@
####
####sumtia/po/Sumtia.notraslated.pot: sumtia/po/Sumtia.pot
####	msgmerge --no-fuzzy-matching mainline/po/es.po $< | msgattrib --no-obsolete --untranslated > $@
####
####followme/po/FollowMe.notraslated.pot: followme/po/FollowMe.pot
####	msgmerge --no-fuzzy-matching mainline/po/es.po $< | msgattrib --no-obsolete --untranslated > $@
####
####
###### update de es.po files of plugins using the pot of not already translated
####updatepo: $(PO_FILES)
####
####butia/po/es.po: butia/po/Butia.notraslated.pot
####	msgmerge --update --no-fuzzy-matching  $@ $<
####
####sumtia/po/es.po: sumtia/po/Sumtia.notraslated.pot
####	msgmerge --update --no-fuzzy-matching  $@ $<
####
####followme/po/es.po: followme/po/FollowMe.notraslated.pot
####	msgmerge --update --no-fuzzy-matching  $@ $<
####
####
##################### END  DEPRECATED!!!!! ###########################



################ Support for lua (bobot-server) ######################

butiaXO:
	# I want butiaXO folder be OK! (needed by plugin)
	make -C ../butiaXO


################ Construction...

mktmpfolder:
	#making folders and copying mainline
	rm -rf tmp
	cp -rL mainline tmp
	rm -rf tmp/.git
	rm -f tmp/.gitignore
	# lets patch the activity.info and add some icons (TurtleBlocks => TurtleBots)
	cp -rLf stagin/activity tmp/

apply_localization: walterGIT mktmpfolder extrasGIT
	# let's add localization (if is not already in taextras.py)
	(cd turtle-extras && ./merge.py turtlebots)
	cp turtle-extras/taextras.py tmp
	# fix localization (compile .po)
	(cd tmp && python setup.py build)
	#msgcat butia/po/es.po tmp/po/es.po -o tmp/po/es.po
	#msgcat sumtia/po/es.po tmp/po/es.po -o tmp/po/es.po
	#msgcat followme/po/es.po tmp/po/es.po -o tmp/po/es.po
	#msgcat nxt_plugin/po/es.po tmp/po/es.po -o tmp/po/es.po

apply_hard_plugins: apply_localization butiaXO walterGIT nxtGIT wedoGIT
	cp -rLf butia tmp/plugins/
	cp -rLf sumtia tmp/plugins/
	cp -rLf followme/ tmp/plugins/
	cp -rLf nxt_plugin/ tmp/plugins/
	cp -rLf wedo_plugin/ tmp/plugins/

pattern_detection_compile:
	make -C pattern_detection/library

apply_sym_plugins: walterGIT nxtGIT wedoGIT apply_localization butiaXO pattern_detection_compile
	# let's make symlinks, it lets you, edit and try, more easily!
	ln -s `pwd`/butia tmp/plugins/butia
	ln -s `pwd`/sumtia tmp/plugins/sumtia
	ln -s `pwd`/followme tmp/plugins/followme
	ln -s `pwd`/nxt_plugin tmp/plugins/nxt_plugin
	ln -s `pwd`/wedo_plugin tmp/plugins/wedo_plugin
	ln -s `pwd`/pattern_detection tmp/plugins/pattern_detection

xo: apply_hard_plugins
	# remove .git from NXT plugin
	rm -rf tmp/plugins/nxt_plugin/.git
	rm -f tmp/plugins/nxt_plugin/.gitignore
	# ok, let's make this .xo
	(cd tmp && python setup.py build)
	#dist_xo no work in the tmp folder
	(cd tmp && python setup.py dist_xo)
	cp tmp/dist/*.xo .
	#$(MAKE) clean_tmp


################ Plugins #############

butia_plugin: apply_hard_plugins
	cp stagin/plugins/butia/plugin.info tmp/plugins
	(cd tmp/plugins && tar -czvf butia_plugin.tar.gz butia/* plugin.info)
	rm tmp/plugins/plugin.info
	mv tmp/plugins/butia_plugin.tar.gz .

followme_plugin: apply_hard_plugins
	cp stagin/plugins/followme/plugin.info tmp/plugins
	(cd tmp/plugins && tar -czvf followme_plugin.tar.gz followme/* plugin.info)
	rm tmp/plugins/plugin.info
	mv tmp/plugins/followme_plugin.tar.gz .

nxt_plugin: apply_hard_plugins
	# remove .git from NXT plugin
	rm -rf tmp/plugins/nxt_plugin/.git
	rm -f tmp/plugins/nxt_plugin/.gitignore
	cp stagin/plugins/nxt_plugin/plugin.info tmp/plugins
	cd tmp/plugins && tar -czvf nxt_plugin.tar.gz nxt_plugin/* plugin.info
	rm tmp/plugins/plugin.info
	mv tmp/plugins/nxt_plugin.tar.gz .

wedo_plugin: apply_hard_plugins
	cp stagin/plugins/wedo_plugin/plugin.info tmp/plugins
	cd tmp/plugins && tar -czvf wedo_plugin.tar.gz wedo_plugin/* plugin.info
	rm tmp/plugins/plugin.info
	mv tmp/plugins/wedo_plugin.tar.gz .

plugins: butia_plugin followme_plugin nxt_plugin wedo_plugin


# TODO!!!!! Aply debian policies!!!
install_activity: xo
	sugar-install-bundle *.xo
	$(MAKE) clean_xo

install: apply_hard_plugins

dev: apply_sym_plugins
	rm -rf ~/Activities/TurtleBots.activity
	mkdir -p ~/Activities
	(cd tmp && python setup.py dev)



####### CLEAN STUFF ######


clean:
	$(MAKE) -C ../butiaXO clean
	#$(MAKE) clean_pot
	$(MAKE) clean_tmp
	$(MAKE) clean_plugins
	$(MAKE) clean_xo
	# this remove only if it's a symlink ; don't remove if installed
	rm -f ~/Activities/TurtleBots.activity

clean_tmp:
	rm -rf tmp

####clean_pot:
####	rm -f $(POT_FILES) $(POT_NT_FILES)

clean_xo:
	rm -f *.xo

clean_plugins:
	rm -f *.tar.gz

uninstall:
	rm -rf ~/Activities/TurtleBots.activity
	

.SUFFIXES:
.SUFFIXES: .c .o .py .pyc .po .pot

# targets that not represent generated files
.PHONY: all clean clean_tmp clean_pot clean_xo clean_plugins first walterGIT wedoGIT nxtGIT butiaXO mktmpfolder apply_hard_plugins apply_sym_plugins genpot genpot_notraslated updatepo xo install uninstall help butia_plugin followme_plugin nxt_plugin wedo_plugin plugins dev pattern_detection_compile
