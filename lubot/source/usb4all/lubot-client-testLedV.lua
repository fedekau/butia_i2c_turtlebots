#!/usr/bin/lua

local socket = require("socket")


local host, port = "127.0.0.1", 2009
--local host, port = "localhost", 2009

local client = assert(socket.connect(host, port))
client:settimeout(nil) --blocking
--client:settimeout(1)

local function send(s)
	print("sending", s)
	client:send(s.."\n")
	local ret = client:receive()
	print("ret:", ret)
	return ret
end
send("LIST")

while true do
	socket.sleep(1)
	send("CALL ledV prender")
	socket.sleep(4)
	send("CALL ledV apagar")
end


