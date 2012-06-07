# Makefile para instalar todas las dependencias del bobot

all:  dependency
	ln -s ../../serialcomm/lua_bindings/lua_serialcomm.so lua_serialcomm.so
	ln -s ../../lualibusb/libluausb.so libluausb.so
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
