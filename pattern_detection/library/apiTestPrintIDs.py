"""
  Loads the C api and prints the ids of the markers defined in object_data file. 
"""

import patternsAPI


det = patternsAPI.detection()
salida = det.arMultiGetIdsMarker()
print salida
print salida.split(";")
