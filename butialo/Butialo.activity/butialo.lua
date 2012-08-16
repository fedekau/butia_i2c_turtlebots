package.path=package.path..";bobot/?.lua;lib/?.lua"



local stricter=require "stricter"
local bobot = require("bobot")
local array=require("array")
local eventlib=require("events")

local run_shell = function(s)
	local f = io.popen(s) -- runs command
	local l = f:read("*a") -- read output of command
	f:close()
	return l
end

local set_debug
for i, v in ipairs(arg) do
	if v=="DEBUG" then
		set_debug=true 
		table.remove(arg, i)
		break
	end
end
if set_debug then 
	bobot.debugprint = print
	print("Debugging messages enabled")
else
	bobot.debugprint = function() end
end

local myscriptname = arg[1]

--close bobot-server, if running
run_shell("sh -n kill_bobot_server.sh &> /dev/null")

bobot.init()
local baseboards = bobot.baseboards

device ={}

local function get_device_name(d)

--print("DEVICENAME", d.module, d.hotplug, d.handler)
	local board_id, port_id = '', ''
	if #bobot.baseboards>1 then
		board_id='@'..d.baseboard.idBoard
	end
	if d.hotplug then 
		port_id = ':'..d.handler
	end
	
	local n=d.module..board_id..port_id
	
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
	for _, bb in ipairs(bobot.baseboards) do
		bobot.debugprint("===board ", bb.idBoard)
		for _,d in ipairs(bb.devices) do
			local regname = get_device_name(d)
			devices[regname]=d
			devices[#devices+1]=d
			d.name=regname
			bobot.debugprint("=====module ",d.module," name",regname)
		end
		bfound = true
	end
	if not bfound then bobot.debugprint("ls:WARN: No Baseboard found.") end
end



-------------------------------------------
--export stuff
local env = {}
local bobot_devices

env.util = {}
env.util.wait = socket.sleep
env.util.get_time = socket.gettime
env.util.new_array = array.new_array

env.events = eventlib
read_devices_list()
env.devices = devices
for _, n in ipairs(env.devices) do

	local d=env.devices[n]
	bobot.debugprint("adding global", n, d)
	local modulename = n
		--string.upper(string.sub(n, 1, 1))
		--.. string.lower(string.sub(n, 2)) --lleva a "Boton"
	env[modulename]=d
end

for k,v in pairs(_G) do env[k]=v end
--for k,v in pairs(env) do print ('ENV', k, v) end

if myscriptname then
	local myscript
	if myscriptname =="-" then
		myscript = assert(loadstring(io.read("*all")))
	else
		myscript = assert(loadfile(myscriptname))
	end	

	env=stricter.make_fixed_proxy(env)
	setfenv(myscript, env)

	myscript()
else
	env.bobot_devices=bobot_devices
	return env
end


