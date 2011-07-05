#!/bin/lua
require "socket"

local butialo=require "butialo"

local debug = function() end
--local debug=function(...) print("PBT", ...) end

local devices = butialo.bobot_devices

local devicestot, adevices = {}, {}
local f = assert (io.popen ("ls bobot/drivers/*.lua"))
for line in f:lines() do
	devicestot[string.match (line, '^.-/.-/(.+)%.')] = true
end 
f:close()
for module, _ in pairs(devices) do
	devicestot[module] = true
end

for module, _ in pairs(devicestot) do
	adevices[#adevices+1] = module
end

table.sort(adevices)
for _, module in pairs(adevices) do
	device = devices[module]
	if device then
		if device.api then 
			print(module, "Y")
			for func, desc in pairs(device.api) do
				local nparams=#desc.parameters
				local generator = func.."( "
				local comma=""
				for i=1,nparams do
					generator=generator..comma..(desc.parameters[i].rname or "p"..i) --parameters
					comma=","
				end
				generator=generator.." )"
				print ('>',generator)
			end
		end
	else
		local f, err = loadfile("bobot/drivers/"..module..".lua", "(driver)"..module)
		if f then 
			print(module, "N")
if err then debug ('>',err) end
			local d = {
				--some usefull stuff for the drivers to use
				string=string,
				print=print,
				math=math,
				tonumber=tonumber,
				tostring=tostring,
				api={}
			}
			setfenv(f, d) --the driver's environment is the device
			local status, err=pcall(f) 
if err then debug ('>',err) end
			for func, desc in pairs(d.api) do
				local nparams=#desc.parameters
				local generator = func.."( "
				local comma=""
				for i=1,nparams do
					generator=generator..comma..(desc.parameters[i].rname or "p"..i) --parameters
					comma=","
				end
				generator=generator.." )"
				print ('>',generator)
			end
		end			
	end
end

