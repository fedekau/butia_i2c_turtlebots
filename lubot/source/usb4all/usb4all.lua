#!/usr/bin/lua
assert(package.loadlib("./libluausb.so","luaopen_libusb"))()

module(..., package.seeall);

local usb4all_baseboard = require("usb4all_baseboard")
BaseBoard = usb4all_baseboard.BaseBoard

local USB4ALL_VENDOR        = 0x04d8
local USB4ALL_PRODUCT       = 0x000c
local USB4ALL_CONFIGURATION = 1
local USB4ALL_INTERFACE     = 0


--baseboards[iSerial] = BaseBoard
baseboards={}

--Returns number of baseboards detected.
function init()
	--refresh devices and buses
	libusb.find_busses()
	libusb.find_devices()

	local buses=libusb.get_busses()
	local n_boards=0
	for dirname, bus in pairs(buses) do 			--iterate buses
		local devices=libusb.get_devices(bus)
		for filename, device in pairs(devices) do	--iterate devices
			local descriptor = libusb.device_descriptor(device)

			--if device is baseboard...
			if ((descriptor.idVendor == USB4ALL_VENDOR) and (descriptor.idProduct == USB4ALL_PRODUCT)) then
				--try to intialize baseboard
				local libusb_handler = libusb.open(device)
				if not libusb_handler then
					print("Error opening device")
					break
				end				
				if not libusb.set_configuration(libusb_handler, USB4ALL_CONFIGURATION) then
					print("Error configuring device")
					break
				end
				if not libusb.claim_interface(libusb_handler, USB4ALL_INTERFACE) then
					print("Error seting device interface")
					break
				end

				--success initializing, instantiate BaseBoard object and register
				local iSerial=descriptor.iSerialNumber
				local bb = BaseBoard:new({idBoard=iSerial, libusb_handler=libusb_handler})
				--bb:force_close_all()
				print("Baseboard:", iSerial)
				baseboards[iSerial]=bb
				n_boards=n_boards+1
			end
		end
	end
	return n_boards
end

init()

