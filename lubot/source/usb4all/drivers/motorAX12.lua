local device = _G
local SET_VEL = string.char(0x00) -- lee la versión del firmware de la placa
local SET_VEL_ANG = string.char(0x01)		-- envia un mensaje a la placa solo para testear la comuncación
local SET_ ANG = string.char(0x02) -- consulta la carga de la batería

api={}
api.setvel = {}
api.setvel.parameters = {[1]={rname="number", rtype="int", min=-1023, max=1023}, [2]={rname="number", rtype="int", min=-1023, max=1023}} --2 bytes que tiene la velocidad del motor
api.setvel.returns = {[1]={rname="ok", rtype="int"}} --one return
api.setvel.call = function (vel)
	local get_set_vel =  SET_VEL .. string.char(vel)
	device:send(get_set_vel) --TODO .. falta poner mas parámetros
	local set_vel_response = device:read(1) 
	local raw_val = string.byte(set_vel_response, 1) 
	return raw_val
end

api={}
api.setvelang = {}
api.setvelang.parameters = {[1]={rname="number", rtype="int", min=-1023, max=1023}, [2]={rname="number", rtype="int", min=-1023, max=1023}, [3]={rname="number", rtype="int", min=-1023, max=1023}, [4]={rname="number", rtype="int", min=-1023, max=1023}} --4 bytes que tiene la velocidad del motor y el ángulo
api.setvelang.returns = {[1]={rname="ok", rtype="int"}} --one return
api.setvelang.call = function (vel, ang)
	local get_set_vel_ang =  SET_VEL_ANG .. string.char(vel) .. string.char(ang)
	device:send(get_set_vel_ang) --TODO .. falta poner mas parámetros
	local set_vel_ang_response = device:read(1) 
	local raw_val = string.byte(set_vel_ang_response, 1) 
	return raw_val
end

api={}
api.setang = {}
api.setang.parameters = {[1]={rname="number", rtype="int", min=-1023, max=1023}, [2]={rname="number", rtype="int", min=-1023, max=1023}} --2 bytes que tienen el ángulo
api.setang.returns = {[1]={rname="ok", rtype="int"}} --one return
api.setang.call = function (ang)
	local get_set_ang =  SET_ANG .. string.char(ang)
	device:send(get_set_ang) 
	local set_ang_response = device:read(1) 
	local raw_val = string.byte(set_ang_response, 1) 
	return raw_val
end
