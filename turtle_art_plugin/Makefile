# Makefile for butia
#
# This program is free to use or modified
# at your ouwn risk
#
# writen by Guillermo Reisch (greisch@fing.edu.uy) and andrew (aaguirre@fing.edu.uy)
# in others words => writen by butia TEAM!


TURTLEARTVERSION=v114

CWD=$(cwd)



cd ..


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
	(cd mainline && git clean -xf) # please eraese any untraged file
	(cd mainline && git reset --hard) # please erase any modific file
	(cd mainline && git checkout $TURTLEARTVERSION)

mkfolders: walterGIT butiaXO
	#making folders and making all
	rm -rf tmp
	cp -rL mainline tmp
	rm -rf tmp/.git
	cp -rLf butia tmp/plugins/
	cp -rLf sumtia tmp/plugins/
	cp -rLf followme/ tmp/plugins/
	cp -rLf stagin/* tmp/
	#lets add localization
	cat mainline/po/es.po butia/po/es.po > tmp/po/es.po

makexo: mkfolders
	# ok, lest make this .xo
	(cd tmp && python setup.py fix_manifest)
	(cd tmp && python setup.py dist_xo)
	cp tmp/dist/*.xo .

all: makexo
	# we finish
	echo FINISH

clean:
	#cleaning all
	rm -rf tmp


# targets that not represent generated files
.PHONY: all clean butiaXO walterGIT makexo mkfolders
