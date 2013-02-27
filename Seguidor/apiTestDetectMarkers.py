"""
  Loads the C api,
    prints the ids of the markers defined in object_data file.
    Queries the api to detect the first defined marker
"""

import multiPatternDetectionAPI

det = multiPatternDetectionAPI.detection()
salida = det.arMultiGetIdsMarker()
markers = salida.split(";")
print "Markers: " + str(markers)
det.init()
i = 0
while i < 5000:
  #det.refresh()
  x = det.getMarkerTrigDist("Stop")
  print x
  print "Padre" + str(i)
  i = i+1

det.cleanup()

print "sali test"
