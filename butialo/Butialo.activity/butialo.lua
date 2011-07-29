package.path=package.path..";bobot/?.lua;lib/?.lua"

local myscriptname = arg[1]

local stricter=require "stricter"
local socket=require "socket"
local bobot = require("bobot")
local array=require("array")
local eventlib=require("events")

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

--close bobot-server, if running
local host, port = "localhost", 2009
local bobotserver = socket.connect(host, port)
if bobotserver then
	bobot.debugprint("Bobot server found, closing...")
	bobotserver:settimeout(nil) --blocking
	bobotserver:send("QUIT\n")
	bobotserver:settimeout(0.5)
	local ret, err = bobotserver:receive()
	if ret then
		bobot.debugprint("Could not close bobot-server:", ret)		
	end
end

bobot.init()
local baseboards = bobot.baseboards

local function get_device_name(devices, n)
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
	local devices={}
	for b_name, bb in pairs(baseboards) do
    		bobot.debugprint("===board ", b_name)
		for d_name,d in pairs(bb.devices) do
			local regname = get_device_name(devices, d_name)
			devices[regname]=d
    			bobot.debugprint("=====d_name ",d_name," regname ",regname)
		end
		bfound = true
	end
	if not bfound then bobot.debugprint ("ls:WARN: No Baseboard found.") end
	return devices
end


local function build_devices()
	
	local bobot_devices = read_devices_list()

	local d = {}
	for modulename, module in pairs(bobot_devices) do
		local device={}
		bobot.debugprint ("+++", modulename)
		if module.api then
			module:open(1,1) --FIXME

			for fname, f in pairs(module.api) do
				bobot.debugprint ("---", fname, f.call)
				device[fname] = f.call
			end

			--local modulename = string.upper(string.sub(modulename, 1, 1))
			--.. string.lower(string.sub(modulename, 2)) --lleva a "Boton"

			d[modulename]=device
			device.name=modulename
		end
	end

	--local meta = { __index}
	--setmetatable(d, meta)
	--setmetatable(n, meta)

	return d, bobot_devices
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
env.devices, bobot_devices = build_devices()
for n, d in pairs(env.devices) do
	bobot.debugprint("adding global", n, d)
	local modulename = string.upper(string.sub(n, 1, 1))
		.. string.lower(string.sub(n, 2)) --lleva a "Boton"
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


