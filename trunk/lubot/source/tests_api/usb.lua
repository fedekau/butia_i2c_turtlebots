#!/usr/bin/lua
module(..., package.seeall);
assert(package.loadlib("./libluausb.so.1.0","luaopen_libusb"))()

--const static int endpoint_in=0x81; /* endpoint 0x81 address for IN */
--const static int endpoint_out=1; /* endpoint 1 address for OUT */

--reads data from the usb
--receives the number of bytes to read. returns the string received from the usb.
--in case of error, returns nil followed by a message.
--TODO add endpoint number as a parameter
function read(n, read_endpoint)
	local ret,err = libusb.recv_usb(n, 81)
	if not ret then
		return nil, err
	end

	return ret
end

--sends data to the usb
--receives the string to be sent. returns true in case of success.
--in case of error, returns nil followed by a message.
--TODO add endpoint number as a parameter
function send(s, send_endpoint)
	local ok, err = libusb.send_usb(string.len(s),s,1)
	return ok, err
end


--Estaría bueno exportar aca otras funcionalidades que brindan los drivers USB genéricos, como ser abrir endpoints, cambio de tipo de transferencia


--Esto se tiene que ir de aca :andres
--requests de firmware version. returns an array with two numbers (major and minor)
--in case of error, returns nil followed by a message.
--function read_version()
--	local ok, err=libusb.send_usb(2,string.char(0x00)..string.char(0x02),string.char(0x01))
--	if not ok then
--		return nil, err
--	end
--	local version,err = libusb.recv_usb(4, string.char(0x81))
--	if not version then
--		return nil, err
--	end
--	if string.byte(version, 1) ~= 0x00 or string.byte(version, 2)~=0x02 then
--		return nil, "Wrong data returned trough USB"
--	end
--
--	return {string.byte(version, 4), string.byte(version, 3)}
--end
