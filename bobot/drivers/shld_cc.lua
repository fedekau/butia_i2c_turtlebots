local device = _G
local RD_VERSION=string.char(0x00)
local SET_VEL_2MTR= 0x01 -- dos motores


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

api.setvel2mtr = {}
api.setvel2mtr.parameters = {[1]={rname="sentido", rtype="int"},[2]={rname="vel", rtype="int"},[3]={rname="sentido", rtype="int"},[4]={rname="vel", rtype="int"}} 
api.setvel2mtr.returns = {[1]={rname="dato", rtype="int"}} --codigo de operación
api.setvel2mtr.call = function (sentido1, vel1, sentido2, vel2)
	vel1, vel2 = tonumber(vel1), tonumber(vel2)
	if vel1>1023 then vel1=1023 end
	if vel2>1023 then vel2=1023 end
	local msg = string.char(SET_VEL_2MTR,sentido1, math.floor(vel1 / 256),vel1 % 256, sentido2, math.floor(vel2 / 256),vel2 % 256)
	device:send(msg)
	local ret = device:read(1)
	local raw_val = string.byte(ret or " ", 1) 	
	return raw_val	 
end

