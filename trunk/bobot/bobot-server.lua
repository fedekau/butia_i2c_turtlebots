#!/usr/bin/lua


package.path=package.path..";./lib/?.lua"

local socket = require("socket")
local process = require("bobot-server-process").process
local http_serve = require("bobot-server-http").serve

local bobot = require("bobot")
--local bobot = require("chotox")

for _, v in ipairs(arg) do
	if v=="debug" then 
		bobot.debugprint = function(...) print(...) end 
		bobot.debugprint("Debugging messages enabled")
		break
	end
end

--tcp listening address
local ADDRESS = "*"
local PORT_B = 2009 --B is for bobot
local PORT_H = 2010 --H is for http

local server_b = assert(socket.bind(ADDRESS, PORT_B))
local server_h = assert(socket.bind(ADDRESS, PORT_H))

local recvt={[1]=server_b, [2]=server_h}

local baseboards = bobot.baseboards

devices = {}

local function get_device_name(n)
	if not devices[n] then
		return n
	end

	local i=2
	local nn=n.."#"..i
	while devices[nn] do
		i=i+1
		nn=n.."#"..i
	end

	return nn
end

local function read_devices_list()
	bobot.debugprint("=Listing Devices")
	local bfound
	devices={}
	for b_name, bb in pairs(baseboards) do
    		bobot.debugprint("===board ", b_name)
		for d_name,d in pairs(bb.devices) do
			local regname = get_device_name(d_name)
			devices[regname]=d
    			bobot.debugprint("=====d_name ",d_name," regname ",regname)
		end
		bfound = true
	end
	if not bfound then bobot.debugprint ("ls:WARN: No Baseboard found.") end
end

function check_open_device(d, ep1, ep2)
	if not d then return end
	if d.handler then
		bobot.debugprint("ls:Already open ", d.name, d.handler)
		return true
	else
		debugprint ("ls:Opening", d.name, d.handler)
		return d:open(ep1 or 1, ep2 or 1) --TODO asignacion de ep?
	end
end

local function split_words(s)
	words={}

	for p in string.gmatch(s, "%S+") do
		words[#words+1	]=p
	end
	
	return words
end

local socket_handlers = {}
setmetatable(socket_handlers, { __mode = 'k' })
socket_handlers[server_b]=function()
	local client, err=server_b:accept()
	if not client then return end
	bobot.debugprint ("bs:New bobot client", client, client:getpeername())
	table.insert(recvt,client)
	socket_handlers[client] = function ()
		local line,err = client:receive()
		if err=='closed' then
			bobot.debugprint ("bs:Closing bobot client", client)
			for k, v in ipairs(recvt) do 
				if client==v then 
					table.remove(recvt,k) 
					return
				end
			end
		end
		if line then
			local words=split_words(line)
			local command=words[1]
			if not command then
				bobot.debugprint("bs:Error parsing line:", line, command)
			else
				if not process[command] then
					bobot.debugprint("bs:Command not supported:", command)
				else
					local ret = process[command](words) or ""
					client:send(ret .. "\n")
				end
			end
		end
	end
end

socket_handlers[server_h]=function()
	local client, err=server_h:accept()
	if not client then return end
	bobot.debugprint ("bs:New http client", client, client:getpeername())
	client:setoption ("tcp-nodelay", true)
	--client:settimeout(5)
	table.insert(recvt,client)			
	socket_handlers[client]	= function ()
		local ret,err=http_serve(client)
		if err=='closed' then
			bobot.debugprint ("bs:Closing http client", client)
			for k, v in ipairs(recvt) do 
				if client==v then 
					table.remove(recvt,k) 
					return
				end
			end
		end
		if ret then 
			client:send(ret)
		end
	end
end


read_devices_list()
print ("Listening...")
-- loop forever waiting for clients

while 1 do
	local recvt_ready, _, err=socket.select(recvt, nil, 1)
	if err~='timeout' then
		local skt=recvt_ready[1]
		socket_handlers[skt]()
	end
end



