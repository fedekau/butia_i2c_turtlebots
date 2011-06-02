#!/usr/bin/lua
module(..., package.seeall);

--local usb=require("usb")
assert(package.loadlib("./../../../lualibusb/Debug/libluausb.so","luaopen_libusb"))()
local USB4ALL_VENDOR        = 0x04d8
local USB4ALL_PRODUCT       = 0x000c
local USB4ALL_CONFIGURATION = 1
local USB4ALL_INTERFACE     = 0
local libusb_handler        = 0

-- USB4all packet protocol:
--_________________________________________________
--|Handler Number|Op type|plength|reserved|Payload|
--|______________|_______|_______|________|_______|
--/-----5bits----/-3bits-/-8bits-/-8bits--/-61byes/

local ADMIN_MODULE_IN_ENDPOINT        			  = 0x01
local ADMIN_MODULE_OUT_ENDPOINT       			  = 0x81
local OPEN_COMMAND                    			  = 0x00
local CLOSE_COMMAND		        	  			  = 0x01
local INIT_COMMAND		        	  			  = 0x07
local CONFIGURE_COMMAND	        	  			  = 0x08
local NULL_BYTE		        		  			  = 0x00
local HEADER_PACKET_SIZE	          			  = 6
local OPEN_RESPONSE_PACKET_SIZE       			  = 5 
local CLOSE_RESPONSE_PACKET_SIZE      			  = 2 
local CONFIGURE_RESPONSE_PACKET_SIZE  			  = 1
local GET_LINES_RESPONSE_PACKET_SIZE			  = 6
local GET_LINE_RESPONSE_PACKET_SIZE				  = 12
local GET_USER_MODULES_SIZE_COMMAND				  = 0x05	
local GET_USER_MODULE_LINE_COMMAND				  = 0x06
local TIMEOUT			        				  = 13
local DEFAULT_PACKET_SIZE 						  = 0x04
local GET_USER_MODULE_LINE_PACKET_SIZE			  = 0x05

function init_usb4all()
    libusb.find_busses()
    libusb.find_devices()
    local buses=libusb.get_busses()
    local last_device
    for dirname, bus in pairs(buses) do
            --print (k)
            local devices=libusb.get_devices(bus)
            for filename, device in pairs(devices) do
                    --print ("bus:", dirname, "device:",filename)
                    local descriptor = libusb.device_descriptor(device)
                    if ((descriptor.idVendor == USB4ALL_VENDOR) and (descriptor.idProduct == USB4ALL_PRODUCT)) then
                       --print("urra");
                       libusb_handler = libusb.open(device)
                       if libusb_handler then
                            res_set_conf = libusb.set_configuration(libusb_handler, USB4ALL_CONFIGURATION)
                            if(res_set_conf) then
                               res_set_iface = libusb.claim_interface(libusb_handler, USB4ALL_INTERFACE)
                               if(res_set_iface) then
                                   print("associated device", libusb_handler);
                               else
                                   print("error seting device interface", res_set_iface)
                               end
                            else
                               print("error configuring device")
                            end
                       else
                          print("error opening device")
                       end
                    last_device=device
                    end
	    end
    end
end

function open_usb4all(module_name)
    local admin_handler_send_command = string.char(0x00); -- first 5 first bits specify handler number and 3 last bits specify operation.
		                     -- In case of open command is atended by admin module in handler 0 and send operation is 000
    local open_packet_length = string.char(HEADER_PACKET_SIZE + string.len(module_name)) 
    local reserved = string.char(NULL_BYTE)	
    local open_command = string.char(OPEN_COMMAND)	
    local admin_module_in_endpoint  = string.char(0x01) -- TODO esto debería pasarse por parámetro
    local admin_module_out_endpoint = string.char(0x01) -- TODO esto debería pasarse por parámetro
    local handler_packet = admin_handler_send_command .. open_packet_length .. reserved
    local admin_packet = open_command .. admin_module_in_endpoint .. admin_module_out_endpoint .. module_name	
    local open_packet  = handler_packet .. admin_packet
    local write_res = libusb.bulk_write(libusb_handler, ADMIN_MODULE_IN_ENDPOINT, open_packet, TIMEOUT)
    if write_res then
	 --print("resultado de write", write_res)
	 local data, err = libusb.bulk_read(libusb_handler, ADMIN_MODULE_OUT_ENDPOINT, OPEN_RESPONSE_PACKET_SIZE, TIMEOUT)	
    	 --if not data then
	 --    print ("read error", err)
	 --    print ("data", data)
	 --    return err
         --else
	     local new_handler = string.byte(data, 5)	
	     -- print ("open result:",new_handler)
	     return new_handler
         --end
    else
        print("libusb write error", write_res)
    end		
end

--TODO necesito una estructura que me mape handler - endpoint
function send_usb4all(handler, data, len)
    local shifted_handler = handler * 8	
    local user_module_handler_send_command = string.char(shifted_handler)   
    local send_packet_length = string.char(0x03 + len)
    local reserved = string.char(NULL_BYTE)		
    local send_packet = user_module_handler_send_command .. send_packet_length .. reserved .. data	
    local write_res = libusb.bulk_write(libusb_handler, 0x01, send_packet, len, TIMEOUT)
    if write_res then
	return write_res
    else
	print("libusb write error", write_res)	
    end
end
	

-- Blocking receive over the User Module
-- Parameter handler is the handler number assigned to the user module when the module is opened
-- Parameter len is the length of the data to be read
-- Returns the buffer readed
function receive_usb4all(handler, len)
    -- desarmo el mapping para saber que endpoint corresponde con el handler	
    local data, err = libusb.bulk_read(libusb_handler, 0x01, len, TIMEOUT)
    return data	
end

function close_usb4all(handler)
    local admin_handler_send_command = string.char(0x00); -- first 5 first bits specify handler number and 3 last bits specify operation.
                                     -- In case of open command is atended by admin module in handler 0 and send operation is 000
    local close_packet_length = string.char(DEFAULT_PACKET_SIZE) --string.char(HEADER_PACKET_SIZE + string.len(module_name))
    local reserved = string.char(NULL_BYTE)
    local close_command = string.char(CLOSE_COMMAND)
    local handler_packet = admin_handler_send_command .. close_packet_length .. reserved
    local admin_packet = close_command .. string.char(handler)
    local close_packet  = handler_packet .. admin_packet
    local write_res = libusb.bulk_write(libusb_handler, ADMIN_MODULE_IN_ENDPOINT, close_packet, TIMEOUT)
    if write_res then
         -- print("resultado de write", write_res)
         local data, err = libusb.bulk_read(libusb_handler, ADMIN_MODULE_OUT_ENDPOINT, CLOSE_RESPONSE_PACKET_SIZE, TIMEOUT)
    else
        print("libusb write error", write_res)
    end
end

function configure_usb4all(handler)
    local admin_handler_send_command = string.char(0x00); -- first 5 first bits specify handler number and 3 last bits specify operation.
                                     -- In case of open command is atended by admin module in handler 0 and send operation is 000
    local configure_packet_length = string.char(DEFAULT_PACKET_SIZE) 
    local reserved = string.char(NULL_BYTE)
    local configure_command = string.char(CONFIGURE_COMMAND)
    local handler_packet = admin_handler_send_command .. configure_packet_length .. reserved
    local admin_packet = configure_command .. string.char(handler) 
    local configure_packet  = handler_packet .. admin_packet
    local write_res = libusb.bulk_write(libusb_handler, ADMIN_MODULE_IN_ENDPOINT, configure_packet, TIMEOUT)
    if write_res then
         print("resultado de write", write_res)
         local data, err = libusb.bulk_read(libusb_handler, ADMIN_MODULE_OUT_ENDPOINT, CONFIGURE_RESPONSE_PACKET_SIZE, TIMEOUT)
    else
        print("libusb write error", write_res)
    end
end


function get_user_modules_size()
	-- first 5 first bits specify handler number and 3 last bits specify operation.
    local admin_handler_send_command = string.char(0x00); 
	-- In case of get_user_modules_size command is atended by admin module in handler 0 and send operation is 000
    local get_user_modules_size_packet_length = string.char(DEFAULT_PACKET_SIZE)
    local reserved = string.char(NULL_BYTE)
    local get_user_modules_size_command = string.char(GET_USER_MODULES_SIZE_COMMAND)
    local handler_packet = admin_handler_send_command .. get_user_modules_size_packet_length .. reserved
    local admin_packet = get_user_modules_size_command 
    local get_user_modules_size_packet  = handler_packet .. admin_packet    
	local write_res = libusb.bulk_write(libusb_handler, ADMIN_MODULE_IN_ENDPOINT, get_user_modules_size_packet, TIMEOUT)
    if write_res then
         -- print("resultado de write", write_res)
         local data, err = libusb.bulk_read(libusb_handler, ADMIN_MODULE_OUT_ENDPOINT, GET_LINES_RESPONSE_PACKET_SIZE, TIMEOUT)
		 local user_modules_size = string.byte(data, 5)	
	     --print ("get_user_modules_size result:",user_modules_size)
	     return user_modules_size
    else	
         print("libusb write error", write_res)
    end
end

function get_user_module_line(line_number)
	-- first 5 first bits specify handler number and 3 last bits specify operation.
    local admin_handler_send_command = string.char(0x00); 
	-- In case of get_user_module_line command is atended by admin module in handler 0 and send operation is 000
    local get_user_module_line_packet_length = string.char(GET_USER_MODULE_LINE_PACKET_SIZE)
    local reserved = string.char(NULL_BYTE)
    local get_user_module_line_command = string.char(GET_USER_MODULE_LINE_COMMAND)
    local handler_packet = admin_handler_send_command .. get_user_module_line_packet_length .. reserved
    local admin_packet = get_user_module_line_command .. string.char(line_number)
    local get_user_module_line_packet  = handler_packet .. admin_packet    
	local write_res = libusb.bulk_write(libusb_handler, ADMIN_MODULE_IN_ENDPOINT, get_user_module_line_packet, TIMEOUT)
    if write_res then
         local data, err = libusb.bulk_read(libusb_handler, ADMIN_MODULE_OUT_ENDPOINT, GET_LINE_RESPONSE_PACKET_SIZE, TIMEOUT)
		 if (err == nil) then
		 	local char_num 
		 	local module_name = ""
		 	for i = GET_USER_MODULE_LINE_PACKET_SIZE, string.len(data)  do
		 		char_num = string.byte(data, i)	
				module_name = module_name .. string.char(char_num)			
		 	end
		 	return module_name .. "\000"
		else
			print("libusb read error", res)
		end
    else	
       	print("libusb write error", write_res)
    end
end

