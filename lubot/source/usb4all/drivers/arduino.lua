local device = _G
local RD_VERSION = string.char(0x00) -- lee la versión del firmware de la placa
local PING = string.char(0x01)		-- envia un mensaje a la placa solo para testear la comuncación
local CARGA_BATERIA = string.char(0x02) -- consulta la carga de la batería
local SETVELMOTORES = string.char(0x03) -- setea la velocidad de ambos motores a la vez

api={}
api.read_version = {}
api.read_version.parameters = {} --no parameters
api.read_version.returns = {[1]={rname="version", rtype="number"}} --one return
api.read_version.call = function ()
	local get_read_version = RD_VERSION 
	device:send(get_read_version)
	local version_response = device:read(1) -- debería leer 1 byte, esta bien?
	local raw_val = string.byte(version_response, 1) --acá tengo que dejarlo en alto nivel?? es decir, divirlo entre 10??
	--print("rawval, deg_temp: ", raw_val, deg_temp)
	return raw_val
end

api.ping = {}
api.ping.parameters = {} --no parameters
api.ping.returns = {[1]={rname ="mensaje", rtype="int"} } -- TODO .. recibo un parametro de nombre mensaje y tipo int
api.ping.call = function ()
	local get_ping = PING
	device:send(get_ping) 
	local ping_response = device:read(1)
	local raw_val = string.byte(ping_response, 1)
	return raw_val
end

api.cargabateria = {}
api.cargabateria.parameters = {} --no parameters
api.cargabateria.returns = {[1]={rname="carga1",rtype="int"}, [2]={rname="carga2", rtype="int"}} --TODO ..el la respuesta esperamos un mensaje con el valor de voltaje de la batería mutiplicado por 10
api.cargabateria.call = function ()
	local get_carga_bateria = CARGA_BATERIA
	device:send(get_carga_bateria)
	local carga_response = device:read(2) -- espero un entero con signo
	local raw_val = string.byte(carga_response,2)
	return raw_val
end


api={}
api.setvelmotores = {}
api.setvelmotores.parameters = {[1]={rname="number", rtype="int", min=-1023, max=1023}, [2]={rname="number", rtype="int", min=-1023, max=1023}} --no parameters
api.setvelmotores.returns = {[1]={rname="ok", rtype="int"}} --one return
api.setvelmotores.call = function (velIzq, velDer)
	local get_set_vel_motores =  SETVELMOTORES .. string.char(velIzq) .. string.char(velDer)
	device:send(get_set_vel_motores) --TODO .. falta poner mas parámetros
	local set_vel_response = device:read(1) 
	local raw_val = string.byte(set_vel_response, 1) 
	return raw_val
end
