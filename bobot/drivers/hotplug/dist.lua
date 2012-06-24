local device = _G

local GET_VALUE=string.char(0x01)
local string_byte=string.byte

api={}
api.getValue = {}
api.getValue.parameters = {} -- -- no input parameters
api.getValue.returns = {[1]={rname="par1", rtype="int"}} 
api.getValue.call = function ()
	device:send(GET_VALUE) -- codigo de operacion 1 = obtener distancia- analog value
	local sen_anl_response = device:read(3) 
	local raw_val	
	if not sen_anl_response or string_byte(sen_anl_response or "00000000", 2) == nil or string_byte(sen_anl_response or "00000000", 3) == nil
	then 
		raw_val = "nil value"
	else
		raw_val = (string_byte(sen_anl_response, 2) or 0)* 256 + (string_byte(sen_anl_response, 3) or 0)
		raw_val = 1024 - raw_val

	end	
	return raw_val  
	
end
