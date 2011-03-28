#!/usr/bin/lua
local usb4all_api=require("usb4all_lua_api")
usb4all_api.init_usb4all()
local cant_user_modules = usb4all_api.get_user_modules_size()
print ("tengo cargados", cant_user_modules, "user_modules")
for i=0, cant_user_modules-1 do
	print ("user_module" ,i, usb4all_api.get_user_module_line(i))
end
