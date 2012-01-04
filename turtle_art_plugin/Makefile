# Makefile for butia
#
# This program is free to use or modified
# at your ouwn risk
#
# writen by Guillermo Reisch (greisch@fing.edu.uy) and andrew (aaguirre@fing.edu.uy)
# in others words => writen by butia TEAM!


TURTLEARTVERSION=fixing

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
	cat butia/po/es.po >> tmp/po/es.po
	cat sumtia/po/es.po >> tmp/po/es.po
	cat followme/po/es.po >> tmp/po/es.po

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
	$(MAKE) -C clean


fakeinstall: apply_sym_plugins
	rm -rf ~/Activities/TurtleArtButia.activity
	mkdir -p ~/Activities
	# ln -s `pwd`/tmp ~/Activities/TurtleArtButia.activity ### setup dev
	# fix localization and index
	(cd tmp && python setup.py fix_manifest)
	(cd tmp && python setup.py dist_xo)
	(cd tmp && python setup.py dev)




#genpot_butia:


#genpot_sumtia:


#genpot_followme: 


#genpot: genpot_followme genpot_sumtia genpot_butia




clean:
	#cleaning all
	rm -rf tmp

cleanall: clean
	make -C ../butiaXO clean





# targets that not represent generated files
.PHONY: all clean cleanall butiaXO walterGIT mktmpfolder apply_hard_plugins apply_sym_plugins makexo
