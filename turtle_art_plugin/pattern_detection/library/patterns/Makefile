INC_DIR= ../ARToolkit/include
LIB_DIR= ../ARToolkit/lib

#LDFLAG=-pthread -lgstreamer-0.10 -lgobject-2.0 -lgmodule-2.0 -lgthread-2.0 -lrt -lxml2 -lglib-2.0 -L/usr/X11R6/lib -L/usr/local/lib -L$(LIB_DIR)
LDFLAG=-pthread -lgstreamer-0.10 -lgobject-2.0 -lglib-2.0 -L/usr/X11R6/lib -L/usr/local/lib -L$(LIB_DIR)
#LIBS= -lARvideo -lAR -lpthread -lXi -lX11 -lm -pthread -lgstreamer-0.10 -lgobject-2.0 -lgmodule-2.0 -lgthread-2.0 -lrt -lxml2 -lglib-2.0 
LIBS= -lARvideo -lAR -lpthread -lm -pthread -lgstreamer-0.10 -lgobject-2.0 -lglib-2.0 
CFLAG= -fPIC -O -pthread -I/usr/include/gstreamer-0.10 -I/usr/include/glib-2.0 -I/usr/lib/i386-linux-gnu/glib-2.0/include -I/usr/X11R6/include -I$(INC_DIR)


OBJS = patterns.o object.o 
HEADDERS = object.h patterns.h

all: patternsTest libPatterns.so

libPatterns.so: $(OBJS)
	cc -shared -o libPatterns.so $(OBJS) $(LIBS) -L$(LIB_DIR)

patternsTest: patternsTest.o $(OBJS)
	cc -o patternsTest patternsTest.o $(OBJS) $(LDFLAG) $(LIBS)

patternsTest.o: patternsTest.c $(HEADDERS)
	cc -c $(CFLAG) patternsTest.c

patterns.o: patterns.c $(HEADDERS)
	cc -c $(CFLAG) patterns.c

object.o: object.c $(HEADDERS)
	cc -c $(CFLAG) object.c

clean:
	rm -f *.o
	rm -f *.so
	rm -f patterns
	rm -f patternsTest

.PHONY: all clean patternsTest
	
