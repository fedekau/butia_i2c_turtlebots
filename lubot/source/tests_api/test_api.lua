#!/usr/bin/lua
local usb4all_api=require("usb4all_lua_api")
usb4all_api.init_usb4all()
local module_name = "temp\000"
print (module_name)
local handler = usb4all_api.open_usb4all(module_name)
print (handler)
local get_temp_payload = string.char(0x34) .. string.char(0x02)
usb4all_api.send_usb4all(handler, get_temp_payload, string.len(get_temp_payload))
local temperature_response = usb4all_api.receive_usb4all(handler,6) 
print (string.byte(temperature_response, 5))
print (string.byte(temperature_response, 6))
local raw_val = string.byte(temperature_response, 5) + (string.byte(temperature_response, 6) * 256)
print (raw_val)
local raw_temp = raw_val / 8
local deg_temp = raw_temp * 0.0625	
print("rawval, deg_temp: ", raw_val, deg_temp)
usb4all_api.close_usb4all(handler)
--usb4all_api.board_init_usb4all()

