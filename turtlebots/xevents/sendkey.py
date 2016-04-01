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

    _special_keys = {'xe_ctrl': Xlib.XK.XK_Control_L,
                      'xe_shift': Xlib.XK.XK_Shift_L,
                      'xe_alt': Xlib.XK.XK_Alt_L,
                      'xe_alt_gr': Xlib.XK.XK_Alt_R,
                      'xe_left_arrow': Xlib.XK.XK_Left,
                      'xe_right_arrow': Xlib.XK.XK_Right,
                      'xe_up_arrow': Xlib.XK.XK_Up,
                      'xe_down_arrow': Xlib.XK.XK_Down,
                      'xe_f1': Xlib.XK.XK_F1,
                      'xe_f2': Xlib.XK.XK_F2,
                      'xe_f3': Xlib.XK.XK_F3,
                      'xe_f4': Xlib.XK.XK_F4,
                      'xe_f5': Xlib.XK.XK_F5,
                      'xe_f6': Xlib.XK.XK_F6,
                      'xe_f7': Xlib.XK.XK_F7,
                      'xe_f8': Xlib.XK.XK_F8,
                      'xe_f9': Xlib.XK.XK_F9,
                      'xe_f10': Xlib.XK.XK_F10,
                      'xe_f11': Xlib.XK.XK_F11,
                      'xe_spacebar': ' ',
                      'xe_tab': '\t',
                      'xe_return': '\r',
                      'xe_escape': '\e',
                      'xe_enter': '\n',

                      }

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

        key = ""

        splitted = keystroke.split(" ")

        for stroke in splitted:
          stroke.strip()
          if cls._special_keys.has_key(stroke):
            key = cls._display.keysym_to_keycode(cls._special_keys[stroke])
            #print stroke
            #print cls._special_keys[stroke]
          else:
            key,shift_mask = cls._char_to_keycode(stroke)
          
          ext.xtest.fake_input(cls._display, X.KeyPress, key)


        for stroke in reversed(splitted):
          stroke.strip()
          if cls._special_keys.has_key(stroke):
            key = cls._display.keysym_to_keycode(cls._special_keys[stroke])
          else:
            key,shift_mask = cls._char_to_keycode(stroke) 
          
          ext.xtest.fake_input(cls._display, X.KeyRelease, key)

        cls._display.sync()


    @classmethod
    def send_key(cls,key):

        k = ""
        shift_mask = 0


        if ((key == "xe_left_arrow") or (key == "xe_right_arrow")
          or (key == "xe_up_arrow") or (key == "xe_down_arrow")):

            k = cls._display.keysym_to_keycode(cls._special_keys[key])
        elif ((key == "xe_spacebar") or (key == "xe_tab") or 
              (key == "xe_return") or (key == "xe_escape") or 
              (key == "xe_enter")):

            k, shift_mask = cls._char_to_keycode(cls._special_keys[key])
       
        else:
            k, shift_mask = cls._char_to_keycode(key)

        shift_keycode = cls._display.keysym_to_keycode(Xlib.XK.XK_Shift_L)


        if shift_mask != 0:
          ext.xtest.fake_input(cls._display, X.KeyPress, shift_keycode)

        ext.xtest.fake_input(cls._display, X.KeyPress, k)
        ext.xtest.fake_input(cls._display, X.KeyRelease,k)

        if shift_mask != 0:
          ext.xtest.fake_input(cls._display, X.KeyRelease, shift_keycode)

        cls._display.sync()