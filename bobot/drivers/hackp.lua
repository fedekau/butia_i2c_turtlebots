local device = _G
local RD_VERSION = string.char(0x00)
local SET_VALUES = 0x01 -- opcode to set 4pin values
local SET_PIN0 = 0x02 -- opcode to set individual values
local SET_PIN1 = 0x03
local SET_PIN2 = 0x04
local SET_PIN3 = 0x05

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

api.set4pin = {}
api.set4pin.parameters = {[1]={rname="pin1", rtype="int"},[2]={rname="pin2", rtype="int"},[3]={rname="pin3", rtype="int"},[4]={rname="pin4", rtype="int"}} 
api.set4pin.returns = {[1]={rname="dato", rtype="int"}} -- 0 if no error ocurred, -1 instead
api.set4pin.call = function (value3, value2, value1, value0)
    if (value0 == nil) or (value1 == nil) or (value2 == nil) or (value3 == nil) then 
        return -1
    end
    value0, value1, value2, value3 = tonumber(value0), tonumber(value1), tonumber(value2), tonumber(value3)
    if ((value0 ~= 0) and (value0 ~= 1) or (value1 ~= 0) and (value1 ~= 1) or (value2 ~= 0) and (value2 ~= 1) or (value3 ~= 0) and (value3 ~= 1)) then
        return -1
    end
    local msg = string.char(SET_VALUES,value3,value2,value1,value0)
    device:send(msg)
    local ret = device:read(1)
    return 0
end

local function setPin (opcode, value)
    if ((value == nil) or ((value ~= 0) and (value ~= 1))) then
        return -1
    end
    local msg = string.char(SET_PIN0,value)
    device:send(msg)
    local ret = device:read(1)
    return 0
end

api.setpin0 = {}
api.setpin0.parameters = {} 
api.setpin0.returns = {[1]={rname="dato", rtype="int"}} -- 0 if no error ocurred, -1 instead
api.setpin0.call = function (value)
    return setPin(SET_PIN0,value)
end
