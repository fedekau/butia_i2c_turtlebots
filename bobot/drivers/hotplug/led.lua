local device = _G

local RD_VERSION=string.char(0x00)
local SET_LED_ON=string.char(0x01)
local SET_LED_OFF=string.char(0x02)
local string_byte=string.byte

-- description: lets us know button module's version
api={}
api.getVersion = {}
api.getVersion.parameters = {} -- no input parameters
api.getVersion.returns = {[1]={rname="version", rtype="int"}}
api.getVersion.call = function ()
	device:send(RD_VERSION) -- operation code 0 = get version
    local version_response = device:read(3) -- 3 bytes to read (opcode, data)
    if not version_response or #version_response~=3 then return -1 end
    local raw_val = (string_byte(version_response,2) or 0) + (string_byte(version_response,3) or 0)* 256
    return raw_val
end

-- description: lets us know button's current status
-- input: empty
-- output: button's current status. Possible status: 1 pressed - 0 not pressed
api.turnOn = {}
api.turnOn.parameters = {} -- no input parameters
api.turnOn.returns = {[1]={rname="state", rtype="int"}}
api.turnOn.call = function ()
	device:send(SET_LED_ON) -- operation code 1 = prender led
	local sen_dig_response = device:read(2) -- 2 bytes to read (opcode, data)
   	if not sen_dig_response or #sen_dig_response~=2 then return -1 end
	local raw_val = string_byte(sen_dig_response, 2) or 0 -- keep data
	return raw_val 
end

-- description: lets us know button's current status
-- input: empty
-- output: button's current status. Possible status: 1 pressed - 0 not pressed
api.turnOff = {}
api.turnOff.parameters = {} -- no input parameters
api.turnOff.returns = {[1]={rname="state", rtype="int"}}
api.turnOff.call = function ()
	device:send(SET_LED_OFF) -- operation code 1 = prender led
	local sen_dig_response = device:read(2) -- 2 bytes to read (opcode, data)
    if not sen_dig_response or #sen_dig_response~=2 then return -1 end
	local raw_val = string_byte(sen_dig_response, 2) or 0 -- keep data
	return raw_val 
end
