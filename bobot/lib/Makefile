# Makefile para instalar todas las dependencias del bobot

all:  dependency
	@echo bobot listo para usar !

dependency:
	$(MAKE) -C ../../serialcomm/lua_bindings
#ifdef USB4ALL
	$(MAKE) -C ../../lualibusb
#endif

clean:
	@rm -f *~ *.o drivers/*~
	$(MAKE) -C ../../serialcomm/lua_bindings clean
	$(MAKE) -C ../../lualibusb clean
