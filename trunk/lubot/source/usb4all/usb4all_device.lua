#!/usr/bin/lua

module(..., package.seeall);

local usb_bulk_write = usb4all.libusb.bulk_write
local usb_bulk_read = usb4all.libusb.bulk_read

local string_char = string.char
local string_len  = string.len
local string_byte = string.byte

local OPEN_COMMAND		= string_char(0x00)
local CLOSE_COMMAND		= string_char(0x01)
local HEADER_PACKET_SIZE	= 6
local NULL_BYTE			= string_char(0x00)
local ADMIN_MODULE_IN_ENDPOINT	= 0x01
local ADMIN_MODULE_OUT_ENDPOINT	= 0x81
local ADMIN_HANDLER_SEND_COMMAND = string_char(0x00)
local OPEN_RESPONSE_PACKET_SIZE  = 5 
local CLOSE_RESPONSE_PACKET_SIZE = 2 
local TIMEOUT			= 1000 --ms

local READ_HEADER_SIZE		= 3

Device = {
	--some usefull stuff for the drivers to use
	string=string,
	print=print,
	math=math,
	tonumber=tonumber,
	tostring=tostring
}

--Instantiates Device object.
--Attempts to load api from driver
function Device:new(d)
	--parameters sanity check
	assert(type(d)=="table")
	assert(type(d.name)=="string")
	assert(type(d.baseboard)=="table")
	assert(type(d.baseboard.libusb_handler)=="userdata")
	
 	--OO boilerplate
  	setmetatable(d, self)
	self.__index = self

	d.libusb_handler = d.baseboard.libusb_handler --save one indirection

	--attempt to load api from driver
	local f, err = loadfile("./drivers/"..d.name..".lua")
	if f then
		d._G=d
		setfenv(f, d) --the driver's environment is the driver
		f()
	else
		--print("Error loading driver:", err)
	end
	
	return d
end

--opens the device. must be done before sending / reading / etc.
--receives endpoints, which can be ommited if they were provided at Device creation
function Device:open(in_endpoint, out_endpoint)
	--state & parameter sanity check
	assert(self.handler==nil)
	assert(type(self.name)=="string")
	assert(type(in_endpoint)=="number" or type(self.in_endpoint)=="number")
	assert(type(out_endpoint)=="number" or type(self.out_endpoint)=="number")
	assert(type(self.libusb_handler)=="userdata")

	--save for later use
	if in_endpoint then self.in_endpoint = in_endpoint end
	if out_endpoint then self.out_endpoint = out_endpoint end

	local module_name=self.name .."\000" -- usb4all expect null terminated names
	local libusb_handler=self.libusb_handler

	local open_packet_length = string_char(HEADER_PACKET_SIZE + string_len(module_name)) 

	local module_in_endpoint  = string_char(self.in_endpoint)
	local module_out_endpoint = string_char(self.out_endpoint)

	local handler_packet = ADMIN_HANDLER_SEND_COMMAND .. open_packet_length .. NULL_BYTE
	local admin_packet = OPEN_COMMAND .. module_in_endpoint .. module_out_endpoint .. module_name	
	local open_packet  = handler_packet .. admin_packet
	local write_res = usb_bulk_write(libusb_handler, ADMIN_MODULE_IN_ENDPOINT, 
					open_packet, string_len(open_packet), TIMEOUT)

	if not write_res then
		print("u4d:open:libusb write error", write_res)
		return
	end

	local data, err = usb_bulk_read(libusb_handler, ADMIN_MODULE_OUT_ENDPOINT, 
					OPEN_RESPONSE_PACKET_SIZE, TIMEOUT)	
	if not data then
		print ("u4d:open:read error", err)
		return	 
	end

	local handler= string_byte(data, 5)
	--hander -1 meand error
	if handler==255 then
		print ("u4d:open:Already open!",self.name,self.handler)
		return
	else
		print ("u4d:open:Success!",self.name,handler)
		self.handler = handler --self.handler set means device is open
		return true
	end

end

--closes the device
function Device:close()
	if not self.handler then return end	--already closed

	--state sanity check
	assert(type(self.handler)=="number")
	assert(type(self.libusb_handler)=="userdata")

	local libusb_handler=self.libusb_handler

	local close_packet_length = string_char(0x04) --string.char(HEADER_PACKET_SIZE + string.len(module_name))
	local handler_packet = ADMIN_HANDLER_SEND_COMMAND .. close_packet_length .. NULL_BYTE
	local admin_packet = CLOSE_COMMAND .. string_char(self.handler)
	local close_packet  = handler_packet .. admin_packet

	local write_res = usb_bulk_write(libusb_handler, ADMIN_MODULE_IN_ENDPOINT, close_packet, 
					string_len(close_packet), TIMEOUT)
	if not write_res then
		print("u4d:close:libusb write error", write_res)
		return
	end
	local data, err = usb_bulk_read(libusb_handler, ADMIN_MODULE_OUT_ENDPOINT, 
					CLOSE_RESPONSE_PACKET_SIZE, TIMEOUT)

	self.handler = nil
end

--sends data (a string) to device
function Device:send(data)
	--state & parameter sanity check
	assert(type(data)=="string")
	assert(type(self.handler)=="number")
	assert(type(self.in_endpoint)=="number")
	assert(type(self.libusb_handler)=="userdata")

	local len=string_len(data)

	local shifted_handler = self.handler * 8	
	local user_module_handler_send_command = string_char(shifted_handler)   
	local send_packet_length = string_char(0x03 + len)	
	local send_packet = user_module_handler_send_command .. send_packet_length .. NULL_BYTE .. data	

	local write_res, err = usb_bulk_write(self.libusb_handler, self.in_endpoint, send_packet, TIMEOUT)
	if not write_res then
		print("u4d:send:libusb write error", err)	
	end

	return write_res, err
end

--read data (len bytes max) from device
function Device:read(len)
	len = len or 255
	--state & parameter sanity check
	assert(type(len)=="number")
	assert(type(self.handler)=="number")
	assert(type(self.out_endpoint)=="number")
	assert(type(self.libusb_handler)=="userdata")

	local data, err = usb_bulk_read(self.libusb_handler, self.out_endpoint, len+READ_HEADER_SIZE, TIMEOUT)
	if not data then
		print("u4d:read:libusb read error", err)	
	end

	local data_h = string.sub(data, READ_HEADER_SIZE+1, -1) --discard header

	return data_h, err
end
