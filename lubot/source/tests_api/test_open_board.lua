#!/usr/bin/lua
local usb4all_api=require("usb4all_lua_api")
usb4all_api.init_usb4all()
local cant_user_modules = usb4all_api.get_user_modules_size()
print ("tengo cargados", cant_user_modules, "user_modules")
local module_name = ""
local u4all_handler = 0
for h=0, cant_user_modules-1 do
	module_name = usb4all_api.get_user_module_line(h)
	u4all_handler = usb4all_api.open_usb4all(module_name)
	print ("user_module" ,h, module_name, u4all_handler)
end
