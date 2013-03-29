local device = _G
local RD_VERSION = string.char(0x02) -- lee la versión del firmware de la placa (Igual para 1.0 y 2.0)
local GET_VOLT = string.char(0x03) -- obtiene el voltage de la batería (Igual para 1.0 y 2.0)

api={}
api.getVersion = {}
api.getVersion.parameters = {}
api.getVersion.returns = {[1]={rname="data", rtype="string"}}
api.getVersion.call = function (data)
	device:send(RD_VERSION)
    local devolver = -1
	local ret = device:read(2)
    if ret then
        devolver = string.byte(ret , 2) --leo el segundo byte obtenido que tiene la versión (el primero tiene el opcode)
    end
    --local devolver = (string.byte(version_response,2) or 0) + (string.byte(version_response,3) or 0)* 256
	return devolver	
end

api.getVolt = {}
api.getVolt.parameters = {} -- no se envian parámetros
api.getVolt.returns = {[1]={rname="volts", rtype="string"}} --nos devuelve el voltaje de las baterías
api.getVolt.call = function ()
	device:send(GET_VOLT) --envío el código de operación
	local data_in = device:read(2) --leo 2 bytes, primero el código de operación y segundo el voltaje
	local voltaje = string.byte(data_in or "00000000" , 2) --leo el segundo byte obtenido que es el que tiene el voltaje
    if voltaje == 255 then
        return voltaje
    else
	    return (voltaje / 10)
    end
end

--[[
function bytesToString(data)
    local data_hex = ""
    for i=1, string.len(data) do
            data_hex = data_hex .. string.format('%02X', (string.byte(data, i)))
    end
    return data_hex
end
--]]
