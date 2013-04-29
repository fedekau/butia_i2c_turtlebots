local device = _G
local RD_VERSION=string.char(0x00)
local WRITE_INFO = 0x01
local READ_INFO  = 0x02
local char000    = string.char(0,0,0)
local mode='wheel'

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

--- Write info
-- write value in regstart to motor[id]
-- byte id, byte regstart, int value
api.writeInfo = {}
api.writeInfo.parameters = {[1]={rname="id", rtype="number", min=0, max=255},[2]={rname="regstart", rtype="number", min=0, max=49},[3]={rname="value", rtype="number", min=0, max=65536}}
api.writeInfo.returns = {[1]={rname="write_info_return", rtype="number"}} --one return
api.writeInfo.call = function (id, regstart, value)
        id, regstart, value = tonumber(id), tonumber(regstart), tonumber(value)
        local write_info_payload = string.char(WRITE_INFO, id, regstart, math.floor(value / 256), value % 256) 
        device:send(write_info_payload)
        local write_info_response = device:read(2) or char000
        local raw_val = (string.byte(write_info_response, 2) or 0) 
        return raw_val
    end

--- Read info
-- read value in regstart from motor[id]
-- byte id, byte regstart, byte lenght of regstart
-- @return current value ar regstart
-- 0..65535
api.readInfo = {}
api.readInfo.parameters = {[1]={rname="id", rtype="number", min=0, max=255},[2]={rname="regstart", rtype="number", min=0, max=49},[3]={rname="lenght", rtype="number", default=1, min=1, max=2}}
api.readInfo.returns = {[1]={rname="value", rtype="number"}} --one return
api.readInfo.call = function(id, regstart, lenght)
        local lenght = lenght or 1
        local send_response = device:send(string.char(READ_INFO, id, regstart, lenght))
        local value = device:read(3) or char000
        local h_value = string.byte(value, 2)
        local l_value = string.byte(value, 3)
        local value = 256 * h_value + l_value
	    return value
    end

--- Send Raw Packet
-- 
api.sendPacket = {}
api.sendPacket.parameters = {[1]={rname="data", rtype="string", min=0, max=1},[2]={rname="wait_resp", rtype="number", min=0, max=1, default=0}}
api.sendPacket.returns = {[1]={rname="return", rtype="number", default=0}} --one return
api.sendPacket.call = function (pack, wait_resp)
        resp = string.char(wait_resp or 0) 
        local payload = string.char(SEND_RAW)..resp..pack
        device:send(payload)

        local response = device:read(255)
        if not response or #response<2 then return -1 end   --only opcode o nil

        if tonumber(wait_resp) == 0 then return 0 end  --user is not waiting an answer

        local timeout = string.byte(response,3)
        if tonumber(timeout) == 1 then return "timeout!" end

        --ax12 answer:
        local size = string.byte(response,2)    --size
        print("AX12 answer\n:::SIZE = "..size.."\n:::TIMEOUT = "..timeout.."\n")

        local msg = '' --answer
        for i=1,size do
            msg = msg..(string.byte(response,(i+3))).." "
        end
        print(":::MESSAGE\n "..msg)
        return msg
    end

--- Set wheel mode.
--Set the motor to continuous rotation mode.
api.wheelMode = {}
api.wheelMode.parameters = {[1]={rname="id", rtype="number", min=0, max=255}}
api.wheelMode.returns = {}
api.wheelMode.call = function (id )
        id = tonumber(id)
		local ret = device:send(string.char(WRITE_INFO,id,0x06,0x00,0x00))
        local write_info_response = device:read(1) or string.char(0,0)
		local ret = device:send(string.char(WRITE_INFO,id,0x08,0x00,0x00))
        local write_info_response = device:read(1) or string.char(0,0)
        mode='wheel'
    end

--- Set joint mode.
-- Set the motor to joint mode. Angles are provided in degrees,
-- in the full servo coverage (0 - 300 degrees arc)
-- @param min the minimum joint angle (defaults to 0)
-- @param max the maximum joint angle (defaults to 300)
api.jointMode = {}
api.jointMode.parameters = {[1]={rname="id", rtype="number", min=0, max=255},[2]={rname="minimo", rtype="number", min=0, max=1023},[3]={rname="maximo", rtype="number", min=0, max=1023}}
api.jointMode.returns = {}
api.jointMode.call = function (id ,minimo, maximo)
        id = tonumber(id)
        minimo=tonumber(minimo)
        maximo=tonumber(maximo)
		local ret = device:send(string.char(WRITE_INFO,id,0x06,math.floor(minimo / 256),minimo % 256))
        local write_info_response = device:read(1) or string.char(0,0)
		local ret = device:send(string.char(WRITE_INFO,id,0x08,math.floor(maximo / 256),maximo % 256))
        local write_info_response = device:read(1) or string.char(0,0)
        mode='joint'
    end


--- Set motor position.
-- Set the target position for the motor's axle. Only works in
-- joint mode.
-- @param value Angle in degrees, in the 0 .. 300deg range.
api.setPosition = {}
api.setPosition.parameters = {[1]={rname="id", rtype="number", min=0, max=255},[2]={rname="pos", rtype="number", min=0, max=1023}}
api.setPosition.returns = {}
api.setPosition.call = function (id, pos )
        id = tonumber(id)
        pos = tonumber(pos)
        local ret = device:send(string.char(WRITE_INFO,id,0x1E,math.floor(pos / 256),pos % 256))
        local write_info_response = device:read(1) or string.char(0,0)
    end


--- Get motor position.
-- Read the axle position from the motor.
-- @return The angle in deg. The reading is only valid in the 
-- 0 .. 300deg range
api.getPosition = {}
api.getPosition.parameters = {[1]={rname="id", rtype="number", min=0, max=255},[2]={rname="pos", rtype="number", min=0, max=1023}}
api.getPosition.returns = {[1]={rname="motor_position", rtype="number"}} --one return
api.getPosition.call = function(id)
        local send_response = device:send(string.char(READ_INFO, id ,0x24, 2))
		local value = device:read(3) or char000
        local h_value = string.byte(value, 2)
        local l_value = string.byte(value, 3)
        local raw_angle = 256 * h_value + l_value
		local ang=0.29*(raw_angle) -- deg ?
		return raw_angle 

	end


--- Set motor speed.
-- @param value If motor in joint mode, speed in deg/sec in the 1 .. 684 range 
-- (0 means max available speed). 
-- If in wheel mode, as a fraction of max torque (in the -1 .. 1 range).
api.setSpeed = {}
api.setSpeed.parameters = {[1]={rname="id", rtype="number", min=0, max=255},[2]={rname="speed", rtype="number", min=-1, max=684}}
api.setSpeed.returns = {} --no return
api.setSpeed.call = function(id, speed)
	--if mode=='joint' then
		-- 0 .. 684 deg/sec
		local vel=math.floor(speed * 1.496)
		local lowb = math.floor(vel/ 256)
		local highb = vel % 256
	
		
		--local lowb, highb = get2bytes_unsigned(vel)
		local ret = device:send(id,0x20,string.char(lowb,highb))
		print ("ret= ",ret, " lowb= ", lowb, " highb= ", highb)
		if ret then return ret:byte() end
	--else --mode=='wheel'
		-- -1 ..  +1 max torque
		--local vel=math.floor(speed * 1023)
		--local lowb, highb = get2bytes_signed(vel)
		--local ret = device:send(id,0x20,string.char(lowb,highb))
		--if ret then return ret:byte() end
	--end
end


