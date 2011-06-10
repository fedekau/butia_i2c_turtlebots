#!/bin/lua
require "socket"

local butialo=require "butialo"

local debug = function() end
--local debug=function(...) print("PBT", ...) end

local path = arg[1]

debug("path", path)
local devices = read_devices_list()

if path=="/" then
	for module,_ in pairs(devices) do
		print(module)
	end
	return
else
	local device = devices[path]
	if device and device.api then
		for func, desc in pairs(device.api) do
			local nparams=#desc.parameters
			local generator = func.."( "
			local comma=""
			for i=1,nparams do
				generator=generator..comma..(desc.parameters[i].rname or "p"..i) --parameters
				comma=","
			end
			generator=generator.." )"
			print (generator)
		end
	end
end
