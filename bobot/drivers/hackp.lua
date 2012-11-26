local device = _G
local string_byte=string.byte
local RD_VERSION = string.char(0x00)
local SET_27_TO_30 = 0x01 -- opcode to set 4pin values
local SET_PIN27 = 0x02 -- opcode to set individual values
local SET_PIN28 = 0x03
local SET_PIN29 = 0x04
local SET_PIN30 = 0x05
local GET_PIN27 = 0x06 -- opcode to get pin values
local GET_PIN28 = 0x07
local GET_PIN29 = 0x08
local GET_PIN30 = 0x09

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
api.set4pin.parameters = {[1]={rname="value3", rtype="int"},[2]={rname="value2", rtype="int"},[3]={rname="value1", rtype="int"},[4]={rname="value0", rtype="int"}} 
api.set4pin.returns = {[1]={rname="dato", rtype="int"}} -- 0 if no error ocurred, -1 instead
api.set4pin.call = function (value3, value2, value1, value0)
    if (value0 == nil) or (value1 == nil) or (value2 == nil) or (value3 == nil) then 
        return -1
    end
    value0, value1, value2, value3 = tonumber(value0), tonumber(value1), tonumber(value2), tonumber(value3)
    if ((value0 ~= 0) and (value0 ~= 1) or (value1 ~= 0) and (value1 ~= 1) or (value2 ~= 0) and (value2 ~= 1) or (value3 ~= 0) and (value3 ~= 1)) then
        return -1
    end
    local msg = string.char(SET_27_TO_30,value0,value1,value2,value3)
    device:send(msg)
    local ret = device:read(1)
    return 0
end

local function setPin (opcode, value)
    if (value == nil) or ((value ~= 0) and (value ~= 1)) then
        return -1
    end
    local msg = string.char(opcode)..string.char(value)
    device:send(msg)
    local ret = device:read(1)
    if not ret or #ret ~= 1 then return -1 end
    return 0
end

api.setpin27 = {}
api.setpin27.parameters = {[1]={rname="value", rtype="int"}} 
api.setpin27.returns = {[1]={rname="dato", rtype="int"}} -- 0 if no error ocurred, -1 instead
api.setpin27.call = function (value)
    return setPin(SET_PIN27,tonumber(value))
end

api.setpin28 = {}
api.setpin28.parameters = {[1]={rname="value", rtype="int"}} 
api.setpin28.returns = {[1]={rname="dato", rtype="int"}} -- 0 if no error ocurred, -1 instead
api.setpin28.call = function (value)
    return setPin(SET_PIN28,tonumber(value))
end

api.setpin29 = {}
api.setpin29.parameters = {[1]={rname="value", rtype="int"}} 
api.setpin29.returns = {[1]={rname="dato", rtype="int"}} -- 0 if no error ocurred, -1 instead
api.setpin29.call = function (value)
    return setPin(SET_PIN29,tonumber(value))
end

api.setpin30 = {}
api.setpin30.parameters = {[1]={rname="value", rtype="int"}} 
api.setpin30.returns = {[1]={rname="dato", rtype="int"}} -- 0 if no error ocurred, -1 instead
api.setpin30.call = function (value)
    return setPin(SET_PIN30,tonumber(value))
end

local function getPin (opcode)
    local msg = string.char(opcode)
    device:send(msg)
    local ret = device:read(2)
    if not ret or #ret ~= 2 then return -1 end
    return string_byte(ret,2) or 0
end

api.getpin27 = {}
api.getpin27.parameters = {} 
api.getpin27.returns = {[1]={rname="dato", rtype="int"}} -- value of pin
api.getpin27.call = function ()
    return getPin(GET_PIN27)
end

api.getpin28 = {}
api.getpin28.parameters = {} 
api.getpin28.returns = {[1]={rname="dato", rtype="int"}} -- value of pin
api.getpin28.call = function ()
    return getPin(GET_PIN28)
end

api.getpin29 = {}
api.getpin29.parameters = {} 
api.getpin29.returns = {[1]={rname="dato", rtype="int"}} -- value of pin
api.getpin29.call = function ()
    return getPin(GET_PIN29)
end

api.getpin30 = {}
api.getpin30.parameters = {}
api.getpin30.returns = {[1]={rname="dato", rtype="int"}} -- value of pin
api.getpin30.call = function ()
    return getPin(GET_PIN30)
end
