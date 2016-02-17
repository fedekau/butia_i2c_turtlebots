# Fuente: http://ubuntueasysetuper.googlecode.com/svn/trunk/FutureWork/sendkey.py

import Xlib
from Xlib import display
from Xlib import XK
from Xlib import X
from Xlib import ext
from Xlib.ext import xtest

class SendKey:

    _special_X_keysyms = {' ': "space",
                                   '\t': "Tab",
                                   '\n': "Return",  # for some reason this needs to be cr, not lf
                                   '\r': "Return",
                                   '\e': "Escape",
                                   '!': "exclam",
                                   '#': "numbersign",
                                   '%': "percent",
                                   '$': "dollar",
                                   '&': "ampersand",
                                   '"': "quotedbl",
                                   '\'': "apostrophe",
                                   '(': "parenleft",
                                   ')': "parenright",
                                   '*': "asterisk",
                                   '=': "equal",
                                   '+': "plus",
                                   ',': "comma",
                                   '-': "minus",
                                   '.': "period",
                                   '/': "slash",
                                   ':': "colon",
                                   ';': "semicolon",
                                   '<': "less",
                                   '>': "greater",
                                   '?': "question",
                                   '@': "at",
                                   '[': "bracketleft",
                                   ']': "bracketright",
                                   '\\': "backslash",
                                   '^': "asciicircum",
                                   '_': "underscore",
                                   '`': "grave",
                                   '{': "braceleft",
                                   '|': "bar",
                                   '}': "braceright",
                                   '~': "asciitilde"}

    _display = display.Display()
    _screen = _display.screen()

    def __init__(self):
        pass

    @classmethod
    def _get_keysym(cls, ch):

        keysym = XK.string_to_keysym(ch)
        if keysym == 0:
            # Unfortunately, although this works to get the correct keysym
            # i.e. keysym for '#' is returned as "numbersign"
            # the subsequent display.keysym_to_keycode("numbersign") is 0.
            #print "b:" + cls._special_X_keysyms[ch]
            keysym = XK.string_to_keysym(cls._special_X_keysyms[ch])
            #print "keysim:" + str(keysym)
        return keysym

    @classmethod
    def _char_to_keycode(cls,ch):

        keysym = cls._get_keysym(ch)
        #	print keysym
        keycode = cls._display.keysym_to_keycode(keysym)
        #	if keycode == 0 :
        #		print "Sorry, can't map", ch
        #	print keycode
        if cls._is_shifted(ch):
          shift_mask = X.ShiftMask
        else:
          shift_mask = 0  

        return keycode, shift_mask

    @classmethod
    def _is_shifted(cls,ch):
      
      return ch.isupper() or ("!\"$%&/()=".find(ch) >= 0)
      

    @classmethod
    def send_special_key(cls,keystroke):

        special_key = ""
        key = ""

        splitted = keystroke.split(" ")

        for stroke in splitted:
            if stroke == "Ctrl":
                special_key = cls._display.keysym_to_keycode(Xlib.XK.XK_Control_L)
            elif stroke == "Shift":
                special_key = cls._display.keysym_to_keycode(Xlib.XK.XK_Shift_L)
            elif stroke == "Alt":
                special_key = cls._display.keysym_to_keycode(Xlib.XK.XK_Alt_L)
            elif stroke == "Space":
                key = cls._char_to_keycode(" ")
            else:  # an ordinary key
                key,shift_mask = cls._char_to_keycode(stroke)

        ext.xtest.fake_input(cls._display, X.KeyPress, special_key)

        ext.xtest.fake_input(cls._display, X.KeyPress, key)
        ext.xtest.fake_input(cls._display, X.KeyRelease, key)

        ext.xtest.fake_input(cls._display, X.KeyRelease, special_key)

        cls._display.sync()


    @classmethod
    def send_key(cls,key):

        k = ""
        shift_mask = 0

        '''xx = XK.string_to_keysym("asterisk")
        xxx = cls._display.keysym_to_keycode(xx)
        print "xx" + str(xx)
        print "xxx" + str(xxx)

        print cls._display.keycode_to_keysym(63,0)
        print cls._display.keycode_to_keysym(63,1)
        print cls._display.keycode_to_keysym(63,2)
        print cls._display.keycode_to_keysym(63,3)'''

        if (key == "Left"):
            k = cls._display.keysym_to_keycode(Xlib.XK.XK_Left)
        elif (key == "Right"):
            k = cls._display.keysym_to_keycode(Xlib.XK.XK_Right)
        elif (key == "Up"):
            k = cls._display.keysym_to_keycode(Xlib.XK.XK_Up)
        elif (key == "Down"):
            k = cls._display.keysym_to_keycode(Xlib.XK.XK_Down)
            '''elif (key == "/"):
                k = cls._display.keysym_to_keycode(Xlib.XK.XK_question)
                print "keysim :" + str(Xlib.XK.XK_question)
                print "keycode:" + str(k)

                k2 = cls._display.keysym_to_keycodes(Xlib.XK.XK_question)
                print "k2:"
                for i in k2:
                  print i

                mapping = cls._display.get_keyboard_mapping(40,100)
                print "mapping:"
                for j in mapping:
                  print j
            '''      
        else:
            k, shift_mask = cls._char_to_keycode(key)


        shift_keycode = cls._display.keysym_to_keycode(Xlib.XK.XK_Shift_L)

        if shift_mask != 0:
          ext.xtest.fake_input(cls._display, X.KeyPress, shift_keycode)
          #print "apreto shift"

        #print k
        ext.xtest.fake_input(cls._display, X.KeyPress, k)
        ext.xtest.fake_input(cls._display, X.KeyRelease,k)

        if shift_mask != 0:
          ext.xtest.fake_input(cls._display, X.KeyRelease, shift_keycode)

        cls._display.sync()