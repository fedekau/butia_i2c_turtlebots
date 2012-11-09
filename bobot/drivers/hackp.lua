local device = _G
local RD_VERSION = string.char(0x00)
local SET_VALUES = 0x01 -- opcode to set 4pin values
local SET_PIN_1 = 0x02
local SET_PIN_2 = 0x03
local SET_PIN_3 = 0x04
local SET_PIN_4 = 0x05

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

api.set4pinValues = {}
api.set4pinValues.parameters = {[1]={rname="pin1", rtype="int"},[2]={rname="pin2", rtype="int"},[3]={rname="pin3", rtype="int"},[4]={rname="pin4", rtype="int"}} 
api.set4pinValues.returns = {[1]={rname="dato", rtype="int"}} -- 0 if no error ocurred, -1 instead
api.set4pinValues.call = function (pin1, pin2, pin3, pin4)
	pin1, pin2, pin3, pin4 = tonumber(pin1), tonumber(pin2), tonumber(pin3), tonumber(pin4)
    if ((pin1 ~= 0) and (pin1 ~= 1) or (pin2 ~= 0) and (pin2 ~= 1) or (pin3 ~= 0) and (pin3 ~= 1) or (pin4 ~= 0) and (pin4 ~= 1)) then
        return -1
    end
	local msg = string.char(SET_VALUES,pin1,pin2,pin3,pin4)
	device:send(msg)
	local ret = device:read(1)
    return 0
end
