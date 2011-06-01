#!/usr/bin/lua

module(..., package.seeall);

local bobot = require("bobot")

--local devices=devices
--local DEBUG = false

process = {}

process["INIT"] = function () --to check the new state of hardware on the fly
    bobot.init()    
    baseboards = bobot.baseboards
    read_devices_list()
end
process["LIST"] = function ()
	local ret,comma = "", ""
	for d_name, _ in pairs(devices) do
		ret = ret .. comma .. d_name
		comma=","
	end
	return ret
end
process["OPEN"] = function (parameters)
	local d  = parameters[2]
	local ep1= tonumber(parameters[3])
	local ep2= tonumber(parameters[4])

	if not d then
		bobot.debugprint("ls:Missing 'device' parameter")
		return
	end
	
	local device = devices[d]
	if check_open_device(device, ep1, ep2) then	
		return "ok"
	else
		return "fail"
	end
end
process["DESCRIBE"] = function (parameters)
	local d  = parameters[2]
	local ep1= tonumber(parameters[3])
	local ep2= tonumber(parameters[4])

	if not d then
		bobot.debugprint("ls:Missing \"device\" parameter")
		return
	end
	
	local device = devices[d]
	if not check_open_device(device, ep1, ep2) then	
		return "fail"
	end
	if not device.api then
		return "missing driver"
	end

	local ret = "{"
	for fname, fdef in pairs(device.api) do
		ret = ret .. fname .. "={"
		ret = ret .. " parameters={"
		for i,pars in ipairs(fdef.parameters) do
			ret = ret .. "[" ..i.."]={"
			for k, v in pairs(pars) do
				ret = ret .."['".. k .."']='"..tostring(v).."',"
			end
			ret = ret .. "},"
		end
		ret = ret .. "}, returns={"
		for i,rets in ipairs(fdef.returns) do
			ret = ret .. "[" ..i.."]={"
			for k, v in pairs(rets) do
				ret = ret .."['".. k .."']='"..tostring(v).."',"
			end
			ret = ret .. "},"
		end
		ret = ret .. "}}," 
	end
	ret=ret.."}"

	return ret
end
process["CALL"] = function (parameters)
	local d  = parameters[2]
	local call  = parameters[3]

	if not (d and call) then
		bobot.debugprint("ls:Missing parameters", d, call)
		return
	end

	local device = devices[d]
	if not check_open_device(device, nil, nil) then	
		return "fail"
	end

	if not device.api then return "missing driver" end
	local api_call=device.api[call];
	if not api_call then return "missing call" end
	
	if api_call.call then
		--local tini=socket.gettime()
		local ok, ret = pcall (api_call.call, unpack(parameters,4))
		if not ok then bobot.debugprint ("Error calling", ret) end
		--print ('%%%%%%%%%%%%%%%% bobot-server',socket.gettime()-tini)
		return ret
	end
end
process["CLOSEALL"] = function ()
	if baseboards then
		for _, bb in pairs(baseboards) do
			-- guille: I dont undestain this part? ;
			-- in the master:HEAD is not commented the second line
			-- but is comented in branch bobot2 ; sow... That i do?
			-- TODO check if delete or not the next line
			---bb:close_all()
			bb:force_close_all() --modif andrew
		end
	end
	return "ok"
end
process["DEBUG"] = function (parameters) --disable debug mode Andrew code!
	local debug = parameters[2]
	if not debug then return "missing parameter" end
	if debug=="ON" then
		bobot.debugprint = function(...) print (...) end  --enable printing
	elseif debug=="OFF" then
		bobot.debugprint = function() end  --do not print anything
	end
	return "ok"
end


