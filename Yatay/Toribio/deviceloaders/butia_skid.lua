--- Library for accesing the accelerometer of a XO 1.75.
-- The device will be named "xo\_accel", module "xo\_accel". 
-- @module xo_accel
-- @alias device

local M = {}
local log = require 'log'

--- Initialize and starts the module.
-- This is called automatically by toribio if the _load_ attribute for the module in the configuration file is set to
-- true.
-- @param conf the configuration table (see @{conf}).
M.init = function(conf)
    local left_run = conf.left_run
    local left_dutty = conf.left_duty
    local left_period = conf.left_period
    local right_run = conf.right_run
    local right_dutty = conf.right_duty
    local right_period = conf.right_period

     --init period, duty and run
    local f_left_duty=io.open(left_dutty,'w')
    local f_left_period=io.open(left_period,'w')
    local f_left_run=io.open(left_run,'w')
    local f_right_duty=io.open(right_dutty,'w')
    local f_right_period=io.open(right_period,'w')
    local f_right_run=io.open(right_run,'w')
    if not f_left_period or not f_left_duty or not f_left_run then return end
    if not f_right_period or not f_right_duty or not f_right_run then return end

    io.output(f_left_period)
    io.write("20000000")
    io.close(f_left_period)

    io.output(f_left_duty)
    io.write("0")	
    io.close(f_left_duty)

    io.output(f_left_run)
    io.write("1")
    io.close(f_left_run)

    io.output(f_right_period)
    io.write("20000000")
    io.close(f_right_period)

    io.output(f_right_duty)
	io.write("0")   
	io.close(f_right_duty)

    io.output(f_right_run)
    io.write("1")
    io.close(f_right_run)

    --Utils
    local function calculate_vel(vel)
        if vel>0 then
            return (2800*vel+1470000)
        end
	if vel<0 then
            return (1470000-3200*-vel)
        else
            return 0
        end
    end

	
    local device={
	name="butia_skid",
	module="butia_skid",


	set_vel = function(vel_right ,vel_left)
        	duty_left = calculate_vel(vel_left)
        	duty_right = calculate_vel(vel_right)
--		print(duty_left)
--		print(duty_right)

		local f_left_duty=io.open(left_dutty,'w')
		local f_right_duty=io.open(right_dutty,'w')
                
		if not f_left_duty or not f_right_duty then return end

        	io.output(f_left_duty)
		io.write(duty_left)
		io.close(f_left_duty)

        	io.output(f_right_duty)
        	io.write(duty_right)
        	io.close(f_right_duty)
		end,
	}

	log('BSKID', 'INFO', 'Device %s created: %s', device.module, device.name)
	local toribio = require 'toribio'
	toribio.add_device(device)
end

return M

--- Configuration Table.
-- This table is populated by toribio from the configuration file.
-- @table conf
-- @field filename device file for the accelerometer (defaults to '/sys/devices/platform/lis3lv02d')

