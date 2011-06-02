local device = _G
local RD_POTE = string.char(0x01)

api={}
api.get_pote = {}
api.get_pote.parameters = {} --no parameter
api.get_pote.returns = {[1]={rname="analog_value", rtype="number"}} --one return
api.get_pote.call = function ()
	local get_pote_payload = RD_POTE 
	device:send(get_pote_payload)
	local pote_response = device:read(3) 
	local raw_val = string.byte(pote_response, 2) + string.byte(pote_response, 3)
	return raw_val
end

