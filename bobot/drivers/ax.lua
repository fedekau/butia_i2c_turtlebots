local device = _G
local WRITE_INFO = 0x01
local char000    = string.char(0,0,0)

--byte id,byte regstart, int value
api={}
api.write_info = {}
api.write_info.parameters = {[1]={rname="id", rtype="number", min=0, max=255},[2]={rname="regstart", rtype="number", min=0, max=255},[3]={rname="value", rtype="number", min=0, max=65536}} ----byte id,byte regstart, int value
api.write_info.returns = {[1]={rname="write_info_return", rtype="number"}} --one return
api.write_info.call = function (id, regstart, value)
    id, regstart, value = tonumber(id), tonumber(regstart), tonumber(value)
    local write_info_payload = string.char(WRITE_INFO, id, regstart, math.floor(value / 256),value % 256) 
    device:send(write_info_payload)
    local write_info_response = device:read(2) or char000
    local raw_val = (string.byte(write_info_response, 2) or 0) 
    return raw_val
end

api.wheel_mode = {}
api.wheel_mode.parameters = {[1]={rname="id", rtype="number", min=0, max=255}}
api.wheel_mode.returns = {}
api.wheel_mode.call = function (id )
        id = tonumber(id)
		local ret = device:send(string.char(WRITE_INFO,id,0x06,0x00,0x00))
        local write_info_response = device:read(1) or string.char(0,0)
		local ret = device:send(string.char(WRITE_INFO,id,0x08,0x00,0x00))
        local write_info_response = device:read(1) or string.char(0,0)
    end

api.joint_mode = {}
api.joint_mode.parameters = {[1]={rname="id", rtype="number", min=0, max=255},[2]={rname="minimo", rtype="number", min=0, max=1023},[3]={rname="maximo", rtype="number", min=0, max=1023}}
api.joint_mode.returns = {}
api.joint_mode.call = function (id ,minimo, maximo)
        id = tonumber(id)
        minimo=tonumber(minimo)
        maximo=tonumber(maximo)
		local ret = device:send(string.char(WRITE_INFO,id,0x06,math.floor(minimo / 256),minimo % 256))
        local write_info_response = device:read(1) or string.char(0,0)
		local ret = device:send(string.char(WRITE_INFO,id,0x08,math.floor(maximo / 256),maximo % 256))
        local write_info_response = device:read(1) or string.char(0,0)
    end

api.set_position = {}
api.set_position.parameters = {[1]={rname="id", rtype="number", min=0, max=255},[2]={rname="pos", rtype="number", min=0, max=1023}}
api.set_position.returns = {}
api.set_position.call = function (id, pos )
        id = tonumber(id)
        pos = tonumber(pos)
        local ret = device:send(string.char(WRITE_INFO,id,0x1E,math.floor(pos / 256),pos % 256))
        local write_info_response = device:read(1) or string.char(0,0)
    end


