local M = {}

local queue = {}
local scheduled_to_queue = {}
local stop = false

local co_template = [[return 
function ()
	local evaluate, op, reference, callback = _G.evaluate, _G.op, _G.reference, _G.callback
--print('++++',evaluate, op, reference, callback)
	coroutine.yield()
	local value
	while true do
		value = evaluate()
--print('aaaaa', value,op, reference)
		if value #OP# reference then callback(value) end
		coroutine.yield()
	end
end]]

function M.add_event (evaluate, op, reference, callback, eventid)
	eventid=eventid or "event"..math.random(2^30)
	local co_s = string.gsub(co_template, "#OP#", op)
--print (co_s)
	local saveglobal=getfenv(1)
	_G = { evaluate=evaluate, op=op, reference=reference, callback=callback,
		loadstring=loadstring, assert=assert, setfenv=setfenv,
		saveglobal=saveglobal, coroutine=coroutine,_G=_G }
	setfenv( 1, _G )
	local co_f = assert( loadstring( co_s, "loadstring:"..eventid) )()
	local co = coroutine.create( co_f )
	status, err = coroutine.resume(co)
	_G = saveglobal
	setfenv( 1, saveglobal )
	if err then error("Coroutine for '"..eventid.."' died with '"..err.."'") end
	scheduled_to_queue[eventid] = co
--print(co)
end

function M.remove_event(id)
	queue[id]=nil
end

function M.stop()
	stop = true
end

function M.go ()
--os.exit()
	while true do
		for id, co in pairs(queue) do
--print('co', #queue,i, co)
			status, err = coroutine.resume(co)
			if err then 
				error("Coroutine for '"..eventid
				.."' died with '"..err.."'") 
			end
			if stop then return end
		end
		for id, newco in pairs(scheduled_to_queue) do
			queue[id]=newco
			scheduled_to_queue[id] = nil
		end
	end
end

return M
