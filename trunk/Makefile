#


all:
	echo pepe


xo:
	rm -f tbutia.xo
	svn list -R | grep TurtleArtButia.activity | zip -@ tbutia.xo

installXO: tortugarte_install


tortugarte_install:
	rm -f ~/Activities/TurtleArtButia.activity
	ln -s `pwd`/TurtleArtButia.activity ~/Activities/
