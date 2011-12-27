# Makefile for butia
#
# This program is free to use or modified
# at your ouwn risk
#
# writen by Guillermo Reisch (greisch@fing.edu.uy) and andrew (aaguirre@fing.edu.uy)
# in others words => writen by butia TEAM!


TURTLEARTVERSION=v114

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
	(cd .. && git submodule update)
	# goto mainline (Walter code) and check if all is OK!
	(cd mainline && git fetch) #make sure we have the last changes of the git
	# I want a especific version of TurtleArts!
	(cd mainline && git reset --hard) # please erase any modific file
	(cd mainline && git clean -xdf) # please eraese any untraged file
	(cd mainline && git checkout $(TURTLEARTVERSION))

mkfolders: walterGIT butiaXO
	#making folders and making all
	rm -rf tmp
	cp -rL mainline tmp
	rm -rf tmp/.git
	cp -rLf butia tmp/plugins/
	cp -rLf sumtia tmp/plugins/
	cp -rLf followme/ tmp/plugins/
	cp -rLf stagin/* tmp/
	# lets add localization (if is not already in taextras.py)
	cat butia/po/es.po >> tmp/po/es.po
	cat sumtia/po/es.po >> tmp/po/es.po
	cat followme/po/es.po >> tmp/po/es.po

makexo: mkfolders
	# ok, lest make this .xo
	(cd tmp && python setup.py fix_manifest)
	(cd tmp && python setup.py dist_xo)
	cp tmp/dist/*.xo .
	make -C . clean  # erase tmp struct

clean:
	#cleaning all
	rm -rf tmp

cleanall: clean
	make -C ../butiaXO clean

fakeinstall: walterGIT butiaXO
	# create a copy to work!
	rm -rf ~/Activities/TurtleArtButia.activity
	mkdir -p ~/Activities
	cp -rL mainline ~/Activities/TurtleArtButia.activity
	rm -rf ~/Activities/TurtleArtButia.activity/.git
	# lets make symlinks, it lets you, edit and try, lot more ease!
	ln -s $(pwd)/butia ~/Activities/TurtleArtButia.activity/plugins/butia
	ln -s $(pwd)/sumtia ~/Activities/TurtleArtButia.activity/plugins/sumtia
	ln -s $(pwd)/followme ~/Activities/TurtleArtButia.activity/plugins/followme
	# lets patch the activity.info and add some icons (TurtleArt => TurtleArtButia)
	cp -rLf stagin/* ~/Activities/TurtleArtButia.activity/
	# lets add localization (if is not already in taextras.py)
	cat butia/po/es.po >> ~/Activities/TurtleArtButia.activity/po/es.po
	cat sumtia/po/es.po >>  ~/Activities/TurtleArtButia.activity/po/es.po
	cat followme/po/es.po >>  ~/Activities/TurtleArtButia.activity/po/es.po
	# fix localization and index
	(cd ~/Activities/TurtleArtButia.activity && python setup.py fix_manifest)
	(cd ~/Activities/TurtleArtButia.activity && python setup.py dist_xo)


# targets that not represent generated files
.PHONY: all clean cleanall butiaXO walterGIT makexo mkfolders
