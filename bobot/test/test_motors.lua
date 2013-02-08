#!/usr/bin/lua

local socket = require("socket")

--local host, port = "192.168.10.1", 2009
local host, port = "localhost", 2009

local client = assert(socket.connect(host, port))
client:settimeout(nil) --blocking
--client:settimeout(1)

local function send(s)
	print("sending", s)
	local val = client:send(s.."\n")
	--print("val:", val)
	local ret = client:receive()
	print("ret:", ret)
	return ret
end
send("LIST")
socket.sleep(1)
send("OPEN motors")
socket.sleep(1)
while true do
	local vel = math.random(1024)
	local sentido = math.random(1)
	send("CALL motors setvel2mtr 0 "..vel .." 0 " ..vel)
	socket.sleep(2)
	send("CALL motors setvel2mtr 1 "..vel .." 1 " ..vel)
	socket.sleep(2)
	send("CALL motors setvel2mtr 1 "..vel .." 0 " ..vel)
	socket.sleep(2)
	send("CALL motors setvel2mtr 0 "..vel .." 1 " ..vel)
	socket.sleep(2)
	send("CALL motors setvel2mtr 0 0 0 0")
	socket.sleep(2)
end
