#!/usr/bin/lua

module(..., package.seeall);

build = {}

build["temp"] = function (env)
	local device=env._device
	env.read = {}
	env.read.parameters = {}
	env.read.returns = {[1]={rname="temperature", rtype="number"}}
	env.read.call = function ()
		local get_temp_payload = string.char(0x34) .. string.char(0x02)
		device:send(get_temp_payload)
		local temperature_response = device:read(6) 
		local raw_val = string.byte(temperature_response, 5) + (string.byte(temperature_response, 6) * 256)
		local raw_temp = raw_val / 8
		local deg_temp = raw_temp * 0.0625	
		--print("rawval, deg_temp: ", raw_val, deg_temp)
		return deg_temp
	end
end
