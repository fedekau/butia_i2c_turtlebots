#!/bin/lua
require "socket"

local host, port = "localhost", 2009
local bobot = assert(socket.connect(host, port))
bobot:settimeout(nil) --blocking

local debug = function() end
--local debug=function(...) print("PBT", ...) end

local function query_bobot(s)
	debug("sending", s)
	bobot:send(s.."\n")
	local ret = bobot:receive()
	debug("ret:", ret)
	return ret
end


local path = arg[1]

debug("path", path)

if path=="/" then
	local list = query_bobot("LIST")
	for module in string.gmatch(list, "%w+") do
		print(module)
	end
	return
end

local desc = query_bobot("DESCRIBE "..path)
local api=loadstring("return "..desc)()
if not api then
	debug("Failure processing:", desc)
	return
end
for func, desc in pairs(api) do
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

