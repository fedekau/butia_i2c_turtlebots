# Makefile for butia
#
# This program is free to use or modified
# at your ouwn risk
#
# writen by Guillermo Reisch (greisch@fing.edu.uy) and andrew (aaguirre@fing.edu.uy)
# in others words => writen by butia TEAM!


TURTLEARTVERSION=v131

CWD=$(cwd)


all: makexo
	# we finish
	echo FINISH

butiaXO:
	# I want butiaXO folder be OK! (needed by plugin)
	make -C ../butiaXO

walterGIT:
	# ok, lets inits and update the submodules (only works if you are in the root of git)
	(cd .. && git submodule init)
	# (cd .. && git submodule update) .... no please, I dont want fetch and checkout at once!
	# goto mainline (Walter code) and check if all is OK!
	(cd mainline && git fetch) #make sure we have the last changes of the git
	# I want a especific version of TurtleArts!
	(cd mainline && git reset --hard) # please erase any modific file
	(cd mainline && git clean -xdf) # please eraese any untraged file
	(cd mainline && git checkout $(TURTLEARTVERSION))

mktmpfolder: walterGIT
	#making folders and coping mainline
	rm -rf tmp
	cp -rL mainline tmp
	rm -rf tmp/.git
	# lets patch the activity.info and add some icons (TurtleArt => TurtleArtButia)
	cp -rLf stagin/* tmp/

apply_localization: mktmpfolder
	# lets add localization (if is not already in taextras.py)
	msgcat butia/po/es.po tmp/po/es.po -o tmp/po/es.po
	msgcat sumtia/po/es.po tmp/po/es.po -o tmp/po/es.po
	msgcat followme/po/es.po tmp/po/es.po -o tmp/po/es.po

apply_hard_plugins: apply_localization butiaXO
	cp -rLf butia tmp/plugins/
	cp -rLf sumtia tmp/plugins/
	cp -rLf followme/ tmp/plugins/

apply_sym_plugins: apply_localization butiaXO
	# lets make symlinks, it lets you, edit and try, lot more ease!
	ln -s `pwd`/butia tmp/plugins/butia
	ln -s `pwd`/sumtia tmp/plugins/sumtia
	ln -s `pwd`/followme tmp/plugins/followme


makexo: apply_hard_plugins
	# ok, lest make this .xo
	(cd tmp && python setup.py fix_manifest)
	(cd tmp && python setup.py dist_xo)
	cp tmp/dist/*.xo .
	$(MAKE) clean


fakeinstall: apply_sym_plugins
	rm -rf ~/Activities/TurtleArtButia.activity
	mkdir -p ~/Activities
	# ln -s `pwd`/tmp ~/Activities/TurtleArtButia.activity ### setup dev
	# fix localization and index
	(cd tmp && python setup.py fix_manifest)
	(cd tmp && python setup.py dist_xo)
	(cd tmp && python setup.py dev)



########### POT GENERATION AND TRASLATION THINKS ###########

POT_FILES= butia/po/Butia.pot sumtia/po/Sumtia.pot followme/po/FollowMe.pot
POT_PROP= --language=Python --add-comments=TRANS: --keyword=_ --join-existing

POT_NT_FILES= butia/po/Butia.notraslated.pot sumtia/po/Sumtia.notraslated.pot \
              followme/po/FollowMe.notraslated.pot

PO_FILES= butia/po/es.po sumtia/po/es.po followme/po/es.po

genpot: $(POT_FILES)

butia/po/Butia.pot: butia/butia.py
	echo msgid \"\" > $@
	echo msgstr \"\" >> $@
	echo \"Content-Type: text/plain\; charset=UTF-8\\n\" >> $@
	xgettext $(POT_PROP) $< -o $@

sumtia/po/Sumtia.pot: sumtia/sumtia.py
	echo msgid \"\" > $@
	echo msgstr \"\" >> $@
	echo \"Content-Type: text/plain\; charset=UTF-8\\n\" >> $@
	xgettext $(POT_PROP) $< -o $@

followme/po/FollowMe.pot: followme/followme.py
	echo msgid \"\" > $@
	echo msgstr \"\" >> $@
	echo \"Content-Type: text/plain\; charset=UTF-8\\n\" >> $@
	xgettext $(POT_PROP) $< -o $@


genpot_notraslated: $(POT_NT_FILES)

butia/po/Butia.notraslated.pot: butia/po/Butia.pot
	msgmerge --no-fuzzy-matching mainline/po/es.po $< | msgattrib --no-obsolete --untranslated > $@

sumtia/po/Sumtia.notraslated.pot: sumtia/po/Sumtia.pot
	msgmerge --no-fuzzy-matching mainline/po/es.po $< | msgattrib --no-obsolete --untranslated > $@

followme/po/FollowMe.notraslated.pot: followme/po/FollowMe.pot
	msgmerge --no-fuzzy-matching mainline/po/es.po $< | msgattrib --no-obsolete --untranslated > $@



updatepo: $(PO_FILES)

butia/po/es.po: butia/po/Butia.notraslated.pot
	msgmerge --update --no-fuzzy-matching  $@ $<

sumtia/po/es.po: sumtia/po/Sumtia.notraslated.pot
	msgmerge --update --no-fuzzy-matching  $@ $<

followme/po/es.po: followme/po/FollowMe.notraslated.pot
	msgmerge --update --no-fuzzy-matching  $@ $<



####### CLEAN STUFF ######


clean:
	#cleaning all
	rm -rf tmp

cleanall: clean
	$(MAKE) -C ../butiaXO clean
	$(MAKE) clean_pot

clean_pot:
	rm -f $(POT_FILES) $(POT_NT_FILES)




# targets that not represent generated files
.PHONY: all clean cleanall clean_pot butiaXO walterGIT mktmpfolder apply_hard_plugins apply_sym_plugins makexo genpot genpot_notraslated updatepo
