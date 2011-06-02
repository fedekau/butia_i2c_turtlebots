#!/usr/bin/lua
--const static int endpoint_in=0x81; /* endpoint 0x81 address for IN */
--const static int endpoint_out=1; /* endpoint 1 address for OUT */

local usb=require("usb")

print ("Testing usb.send()+usb.read()")
usb.send(string.char(0x00)..string.char(0x02), string.char(0x01))
local data, err=usb.read(4, string.char(0x81))
if data then
	print("version:", string.byte(data,4).."."..string.byte(data,3))
else
	print (err)
end

print ("Testing usb.read_version()")
local version, err=usb.read_version()
if version then
	print("version:", version[1].."."..version[2])
else
	print(err)
end

