from pysvg.structure import *
from pysvg.core import *
from pysvg.text import *
from pysvg import parser

#anSVG = parser.parse('algo.svg')
anSVG = parser.parse('xx2.svg')
print  anSVG.get_height()
print  anSVG.get_width()

anSVG.set_width(120)
anSVG.set_height(120)
#print  anSVG.get_height()
#print  anSVG.get_width()

#anSVG.setAttribute("width","150px")


s=svg(width="200px", height="200px")
#s=svg()
s.addElement(anSVG)
print  s.get_height()
print  s.get_width()

s.save('zz.svg')
