require "socket"

local host, port = "localhost", 2009
local bobot = assert(socket.connect(host, port))
bobot:settimeout(nil) --blocking

local debug = function() end
--local debug=function(...) print("BL", ...) end

function query_bobot(s)
	debug("sending", s)
	bobot:send(s.."\n")
	local ret = bobot:receive()
	debug("ret:", ret)
	return ret
end

local function build_devices()
	local d = {}
	local list = query_bobot("LIST")
	for module in string.gmatch(list, "%w+") do
		local device={}

		local desc=query_bobot("DESCRIBE "..module)
		debug(module, desc)

		local fdesc=loadstring("return "..desc)
		if fdesc then
			local api=fdesc()
			if api then
				for func, desc in pairs(api) do
					--[[
					--TODO generar la funcion en un string para loadstring c/#parametros correcto
					local callstring="CALL "..module.." "..func
					device[func] = function(...)
		 				for _, parameter in ipairs({...}) do
							callstring=callstring.." "..parameter
						end
						return query_bobot(callstring)
					end
					--]]

					debug ("---", func, desc)
	
					local nparams=#desc.parameters
					local generator = "return function("
					local comma=""
					for i=1,nparams do
						generator=generator..comma.."p"..i --parameters
						comma=","
					end
					generator=generator..") callstring='CALL "..module.." " ..func.." '"
					for i=1,nparams do
						generator=generator.."..(".."p"..i.." or '') .. ' '" --parameters
					end
					generator=generator.." return query_bobot(callstring) end"
				
					debug("=========================")
					debug(generator)
					debug("=========================")
			
					device[func] = loadstring(generator)()

				end

				local devicename = string.upper(string.sub(module, 1, 1))
				.. string.lower(string.sub(module, 2)) --lleva a "Boton"

				d[devicename]=device
				device.name=devicename
			end
		end
	end

	--local meta = { __index}
	--setmetatable(d, meta)
	--setmetatable(n, meta)

	return d
end



-------------------------------------------
--export stuff
wait = socket.sleep
DEVICES = build_devices()
for n, d in pairs(DEVICES) do
	debug("adding global", n, d)
	_G[n]=d
end

