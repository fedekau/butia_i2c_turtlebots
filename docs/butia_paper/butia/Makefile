TARGET = jar2010
TEXFILES = $(wildcard *.tex)
EPSFILES = $(patsubst %.fig,%.eps,$(wildcard *.fig))

all: $(EPSFILES) $(TARGET).pdf 

%.pdf: %.tex
	pdflatex $< $@ 
	bibtex $(TARGET)
	pdflatex $< $@ 
	pdflatex $< $@

%.eps: %.fig
	fig2dev -L eps $< > $@

clean:
	-rm *.aux *.bbl *.pdf

force:
	gmake clean
	gmake all

tar:
	-rm $(TARGET).tar $(TARGET).tar.gz
	tar cvf $(TARGET).tar Makefile *.tex *.fig *.bib
	gzip $(TARGET).tar
  


