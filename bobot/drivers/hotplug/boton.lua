local device = _G

local GET_VALUE=string.char(0x01)
local string_byte=string.byte

-- descripción: permite conocer el estado el botón en un momento dado.
-- entrada: no tiene.
-- salida: estado del botón. Posibles estados: 1 presionado, 0 libre.
api={}
api.getValue = {}
api.getValue.parameters = {} -- no tiene parámetros de entrada
api.getValue.returns = {[1]={rname="state", rtype="int"}} -- 1 = presionado, 0 = libre
api.getValue.call = function ()
	device:send(GET_VALUE)		-- codigo de operacion 1 = obtener estado boton
	local sen_dig_response = device:read(2) -- leo 2 bytes (opcode, data)
	local raw_val
	if not sen_dig_response or string_byte(sen_dig_response or "00000000", 2) == nil 
	then 
		raw_val = "nil value"
	else
		raw_val = string_byte(sen_dig_response, 2) -- me quedo con los datos
	end	
	return raw_val 
end
