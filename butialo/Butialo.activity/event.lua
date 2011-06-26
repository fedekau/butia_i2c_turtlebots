local M = {}

local queue = {}
local scheduled_to_queue = {}
local stop = false

local function in_out_range(in_range, evval, op, value, hysteresis)
	local evval_n, value_n=tonumber(evval), tonumber(value)
	--print ("==",in_range,mib, evval..op..value, evval_n, value_n,tostring(evval==value), tostring(evval_n==value_n), hysteresis)
			
	if in_range then
		if ((not evval_n or not value_n ) and 
				op=="==" and evval~=value) 
			or
			(evval_n and value_n and ( 
				(op=="==" and evval_n~=value_n) or
				(op=="~=" and evval_n==value_n) or
				(op==">" and evval_n<=value_n-hysteresis) or
				(op=="<" and evval_n>=value_n+hysteresis) or
				(op=="<=" and evval_n>value_n+hysteresis) or
				(op==">=" and evval_n<value_n+hysteresis)
			)) 
		then
			--exiting range, don't return anything
			--print ("saliendo")
			return false, nil
		else
			--stay in range, don't return anything
			--print ("dentro")
			return true, nil
		end			
	else
		--print ("##"..evval..op..value.."##")
		if (op=="==" and evval==value) or
			(evval_n and value_n and ( 
				(op=="==" and evval_n==value_n) or
				(op=="~=" and evval_n~=value_n) or
				(op==">" and evval_n>value_n) or
				(op=="<" and evval_n<value_n) or
				(op=="<=" and evval_n<=value_n) or
				(op==">=" and evval_n>=value_n)
			)) 
		then
			--entering range, return value
			--print ("entrando")
			return true, evval

		else
			--staying out of range, don't return anything
			--print ("fuera")
			return false, nil
		end
	end
end

local cache_ev = {}

local function value_tracker (evaluate, op, reference, callback, hysteresis)

	local hysteresis = tonumber(hysteresis) or 0

--print("---value", evaluate, op, reference, callback)

	local in_range,ret=false
	local evval, cache_evval
	while true do
		cache_evval = cache_ev[evaluate]
		if cache_evval then
			evval = cache_evval
		else
			evval = evaluate()
			cache_ev[evaluate] = evval
		end

		in_range, ret = in_out_range(in_range, evval, op, reference, hysteresis)
		if ret then
			callback(ret)
		end
		coroutine.yield()
	end
end

function M.add ( evaluate, op, reference, callback, eventid, hysteresis )
	eventid=eventid or "event"..math.random(2^30)
	
	local co = coroutine.create(function ()
	        value_tracker( evaluate, op, reference, callback, hysteresis )
	end)
	scheduled_to_queue[eventid] = co
	return eventid
--print(co)
end

function M.remove(id)
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
			local ok, val = coroutine.resume(co)
			if not ok then 
				error("Coroutine for '"..id
				.."' died with '"..val.."'") 
			end
			if stop then return end
		end
		for id, newco in pairs(scheduled_to_queue) do
			queue[id]=newco
			scheduled_to_queue[id] = nil
		end
		cache_ev = {}
	end
end

return M
