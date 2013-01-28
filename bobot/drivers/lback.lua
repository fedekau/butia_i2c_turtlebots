local device = _G

local RD_VERSION=string.char(0x00)
local SEND_DATA=string.char(0x01)

api={}
api.getVersion = {}
api.getVersion.parameters = {} -- no input parameters
api.getVersion.returns = {[1]={rname="version", rtype="int"}}
api.getVersion.call = function ()
	device:send(RD_VERSION) -- operation code 0 = get version
    local version_response = device:read(3) -- 3 bytes to read (opcode, data)
    if not version_response or #version_response~=3 then return -1 end
    local raw_val = (string.byte(version_response,2) or 0) + (string.byte(version_response,3) or 0)* 256
    return raw_val
end

--[[
api.send = {}
api.send.parameters = {[1]={rname="data", rtype="string"}}
api.send.returns = {}
api.send.call = function (data)
	print("####", data, string.len(data))
	device:send(data)
end

api.read = {}
api.read.parameters = {[1]={rname="len", rtype="int", default=64, min=0, max=255}}
api.read.returns = {[1]={rname="data", rtype="string"}}
api.read.call = function (len)
	local len = len or 64
	local ret = device:read(tonumber(len))
	print("====",ret, string.len(ret))
	return ret
end
--]]

api.send = {}
api.send.parameters = {[1]={rname="data", rtype="string"}}
api.send.returns = {}
api.send.call = function (data)
--    print("#######", data, string.len(data))
	device:send(SEND_DATA..data)
end

api.read = {}
api.read.parameters = {[1]={rname="len", rtype="int", default=64, min=0, max=255}}
api.read.returns = {[1]={rname="data", rtype="string"}}
api.read.call = function (len)
	local len = len or 64
	local ret = device:read(len)
--    print("#######",ret, string.len(ret))
    return ret
end

