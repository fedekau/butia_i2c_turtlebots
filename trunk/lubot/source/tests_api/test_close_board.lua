#!/usr/bin/lua
local usb4all_api=require("usb4all_lua_api")
usb4all_api.init_usb4all()
local cant_user_modules = usb4all_api.get_user_modules_size()
print ("tengo cargados", cant_user_modules, "user_modules")
local module_name = ""
local u4all_handler = 1
for h=0, cant_user_modules-1 do
	usb4all_api.close_usb4all(u4all_handler)
	u4all_handler = u4all_handler + 1
end
