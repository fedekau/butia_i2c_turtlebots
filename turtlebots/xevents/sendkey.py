#Fuente: http://ubuntueasysetuper.googlecode.com/svn/trunk/FutureWork/sendkey.py

try:
	import Xlib
except:
	import os
	print "Run 'sudo apt-get install python-xlib -y'"
	os.system('sudo apt-get install python-xlib -y')
	try:
		import Xlib
	except:
		sys.exit(0)
import Xlib.display
import Xlib.X
import Xlib.XK
import Xlib.protocol.event
import Xlib.ext.xtest

display = Xlib.display.Display()

special_X_keysyms = {
	' ' : "space",
	'\t' : "Tab",
	'\n' : "Return",  # for some reason this needs to be cr, not lf
	'\r' : "Return",
	'\e' : "Escape",
	'!' : "exclam",
	'#' : "numbersign",
	'%' : "percent",
	'$' : "dollar",
	'&' : "ampersand",
	'"' : "quotedbl",
	'\'' : "apostrophe",
	'(' : "parenleft",
	')' : "parenright",
	'*' : "asterisk",
	'=' : "equal",
	'+' : "plus",
	',' : "comma",
	'-' : "minus",
	'.' : "period",
	'/' : "slash",
	':' : "colon",
	';' : "semicolon",
	'<' : "less",
	'>' : "greater",
	'?' : "question",
	'@' : "at",
	'[' : "bracketleft",
	']' : "bracketright",
	'\\' : "backslash",
	'^' : "asciicircum",
	'_' : "underscore",
	'`' : "grave",
	'{' : "braceleft",
	'|' : "bar",
	'}' : "braceright",
	'~' : "asciitilde"
}


def get_keysym(ch) :
	keysym = Xlib.XK.string_to_keysym(ch)
	if keysym == 0 :
		# Unfortunately, although this works to get the correct keysym
		# i.e. keysym for '#' is returned as "numbersign"
		# the subsequent display.keysym_to_keycode("numbersign") is 0.
		keysym = Xlib.XK.string_to_keysym(special_X_keysyms[ch])
	return keysym

def char_to_keycode(ch) :
	keysym = get_keysym(ch)
#	print keysym
	keycode = display.keysym_to_keycode(keysym)
#	if keycode == 0 :
#		print "Sorry, can't map", ch
#	print keycode
	return keycode

ctrlkey=display.keysym_to_keycode(Xlib.XK.XK_Control_L)
altkey=display.keysym_to_keycode(Xlib.XK.XK_Alt_L)
shiftkey=display.keysym_to_keycode(Xlib.XK.XK_Shift_L)

def sendkey(keystroke):
	ctrl = alt = shift = 0
	key = ""
	splitted = keystroke.split(" ")
	for stroke in splitted:
		if stroke == "Ctrl":
			ctrl = 1
		elif stroke == "Shift":
			shift = 1
		elif stroke == "Alt":
			alt = 1
		elif stroke == "Space": 
			key = char_to_keycode(" ")
		else: # an ordinary key
			key = char_to_keycode(stroke)
	if ctrl==1:
		Xlib.ext.xtest.fake_input(display, Xlib.X.KeyPress, ctrlkey)
	if alt==1:
		Xlib.ext.xtest.fake_input(display, Xlib.X.KeyPress, altkey)
	if shift==1:
		Xlib.ext.xtest.fake_input(display, Xlib.X.KeyPress, shiftkey)
	Xlib.ext.xtest.fake_input(display, Xlib.X.KeyPress, key)
	Xlib.ext.xtest.fake_input(display, Xlib.X.KeyRelease, key)
	if ctrl==1:
		Xlib.ext.xtest.fake_input(display, Xlib.X.KeyRelease, ctrlkey)
	if alt==1:
		Xlib.ext.xtest.fake_input(display, Xlib.X.KeyRelease, altkey)
	if shift==1:
		Xlib.ext.xtest.fake_input(display, Xlib.X.KeyRelease, shiftkey)
	display.sync()

