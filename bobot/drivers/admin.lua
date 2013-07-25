local device = _G
local GET_VERSION = string.char(0xFE)
local RESET = string.char(0xFF)

api={}
api.getVersion = {}
api.getVersion.parameters = {}
api.getVersion.returns = {[1]={rname="data", rtype="string"}}
api.getVersion.call = function (data)
	device:send(GET_VERSION)
    local devolver = -1
	local ret = device:read(2)
    if ret then
        devolver = string.byte(ret , 2)
    end
	return devolver	
end

api.reset = {}
api.reset.parameters = {}
api.reset.returns = {}
api.reset.call = function (data)
	device:send(RESET)
end

