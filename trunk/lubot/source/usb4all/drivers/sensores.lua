local device = _G
local SEN_DIG = string.char(0x00) -- consulta un sensor digital
local SEN_ANL = string.char(0x01) -- consulta un sensor analogico 
local SEN_ I2C = string.char(0x02) -- consulta un sensor i2c 

api={}
api.sendig = {}
api.sendig.parameters = {} -- no params
api.sendig.returns = {[1]={rname="par1", rtype="int"}, [2]={rname="par2", rtype="int"}} --two return
api.sendig.call = function ()
	local get_sen_dig =  SET_DIG
	device:send(get_sen_dig) 
	local sen_dig_response = device:read(2) 
	local raw_val = string.byte(set_dig_response, 2) 
	return raw_val
end

api={}
api.senanl = {}
api.senanl.parameters = {} -- no params
api.senanl.returns = {[1]={rname="par1", rtype="int"}, [2]={rname="par2", rtype="int"}} --two return
api.senanl.call = function ()
	local get_sen_anl =  SET_ANL
	device:send(get_sen_anl) 
	local sen_anl_response = device:read(2) 
	local raw_val = string.byte(set_anl_response, 2) 
	return raw_val
end

api={}
api.seni2c = {}
api.seni2c.parameters = {} -- no params
api.seni2c.returns = {[1]={rname="par1", rtype="int"}, [2]={rname="par2", rtype="int"}} --two return
api.seni2c.call = function ()
	local get_sen_i2c =  SET_I2C
	device:send(get_sen_i2c) 
	local sen_i2c_response = device:read(2) 
	local raw_val = string.byte(set_i2c_response, 2) 
	return raw_val
end

