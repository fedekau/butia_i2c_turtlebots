#!/usr/bin/lua
local usb4all_api=require("usb4all_lua_api")
usb4all_api.init_usb4all()
local module_name = "temp\000"
print (module_name)
local handler = usb4all_api.open_usb4all(module_name)
print (handler)
module_name = "dac\000"
print (module_name)
local handler = usb4all_api.open_usb4all(module_name)
print (handler)
module_name = "inch>>\000"
print (module_name)
local handler = usb4all_api.open_usb4all(module_name)
print (handler)

usb4all_api.close_usb4all(handler)

