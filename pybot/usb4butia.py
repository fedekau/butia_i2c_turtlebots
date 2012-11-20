
import usb


# Constantes

USB4ALL_VENDOR        = 0x04d8
USB4ALL_PRODUCT       = 0x000c
USB4ALL_CONFIGURATION = 1
USB4ALL_INTERFACE     = 0

READ_HEADER_SIZE      = 3

# Otras

#CONSTANTS

NULL_BYTE = 0x00
DEFAULT_PACKET_SIZE = 0x04
GET_USER_MODULES_SIZE_COMMAND = 0x05
GET_USER_MODULE_LINE_COMMAND = 0x06
GET_HANDLER_SIZE_COMMAND = 0x0A
GET_HANDLER_TYPE_COMMAND = 0x0B
ADMIN_HANDLER_SEND_COMMAND = 0x00
CLOSEALL_BASE_BOARD_COMMAND = 0x07
SWITCH_TO_BOOT_BASE_BOARD_COMMAND = 0x09
RESET_BASE_BOARD_COMMAND = 0xFF

ADMIN_MODULE_IN_ENDPOINT = 0x01
ADMIN_MODULE_OUT_ENDPOINT = 0x81
GET_USER_MODULE_LINE_PACKET_SIZE = 0x05

GET_LINES_RESPONSE_PACKET_SIZE = 5
GET_LINE_RESPONSE_PACKET_SIZE = 12
GET_HANDLER_TYPE_PACKET_SIZE = 5
GET_HANDLER_RESPONSE_PACKET_SIZE = 5
CLOSEALL_BASE_BOARD_RESPONSE_PACKET_SIZE = 5
TIMEOUT = 250
MAX_RETRY = 5

# BUTIA
RD_VERSION = 0x02
GET_VOLT = 0x03

#################################################



class USB4butia():

    def __init__(self, dev):
        self.device = dev
        self.handle = None
        self.listi = []
        self.hotplug = ['button', 'distanc', 'grey', 'light', 'volt', 'res']
        
    def open_device(self):
        if not self.device:
            print "Unable to find device!"
            return None
        if self.handle == None:
            try:
                self.handle = self.device.open()
                self.handle.setConfiguration(USB4ALL_CONFIGURATION)
                self.handle.claimInterface(USB4ALL_INTERFACE)
            except usb.USBError, err:
                print err
                self.handle = None
        return self.handle

    def close_device(self):
        try:
            self.handle.releaseInterface()
        except Exception, err:
            print err
        self.handle = None
        self.device = None

    def read(self, length, timeout = 0):
        return self.handle.bulkRead(ADMIN_MODULE_OUT_ENDPOINT, length, timeout)
 
    def write(self, buffer, timeout = 0):
        return self.handle.bulkWrite(ADMIN_MODULE_IN_ENDPOINT, buffer, timeout)

    def get_info(self):
        names = self.handle.getString(1, 255)
        copy = self.handle.getString(2, 255)
        sn = self.handle.getString(3, 255)
        return [names, copy, sn]

    #returns number of modules present on baseboard
    def get_user_modules_size(self):
        w = []
        w.append(ADMIN_HANDLER_SEND_COMMAND)
        w.append(DEFAULT_PACKET_SIZE)
        w.append(NULL_BYTE)
        w.append(GET_USER_MODULES_SIZE_COMMAND)
        size = self.write(w, TIMEOUT)

        raw = self.read(GET_USER_MODULE_LINE_PACKET_SIZE, TIMEOUT)

        modules = raw[4]

        return modules

    def get_user_module_line(self, index):
        w = []
        w.append(ADMIN_HANDLER_SEND_COMMAND)
        w.append(GET_USER_MODULE_LINE_PACKET_SIZE)
        w.append(NULL_BYTE)
        w.append(GET_USER_MODULE_LINE_COMMAND)
        w.append(index)
        if index < 0:
            return 'Error'
        size = self.write(w, TIMEOUT)

        raw = self.read(GET_LINE_RESPONSE_PACKET_SIZE, TIMEOUT)
        
        #the name is between a header and a null
        c = raw[4:len(raw)]
        t = ''
        for e in c:
            if not(e == NULL_BYTE):
                t = t + chr(e)

        return t

    # LISTI
    def get_handler_size(self):
        w = []
        w.append(ADMIN_HANDLER_SEND_COMMAND)
        w.append(DEFAULT_PACKET_SIZE)
        w.append(NULL_BYTE)
        w.append(GET_HANDLER_SIZE_COMMAND)
        size = self.write(w, TIMEOUT)

        raw = self.read(GET_HANDLER_RESPONSE_PACKET_SIZE, TIMEOUT)

        return raw[4]

    # LISTI
    def get_handler_type(self, index):
        w = []
        w.append(ADMIN_HANDLER_SEND_COMMAND)
        w.append(GET_HANDLER_TYPE_PACKET_SIZE)
        w.append(NULL_BYTE)
        w.append(GET_HANDLER_TYPE_COMMAND)
        w.append(index)
        size = self.write(w, TIMEOUT)

        raw = self.read(GET_HANDLER_RESPONSE_PACKET_SIZE, TIMEOUT)

        return raw[4]

    def switch_to_bootloader(self):
        w = []
        w.append(ADMIN_HANDLER_SEND_COMMAND)
        w.append(DEFAULT_PACKET_SIZE)
        w.append(NULL_BYTE)
        w.append(SWITCH_TO_BOOT_BASE_BOARD_COMMAND)
        size = self.write(w, TIMEOUT)
        # nothing to return

    def reset(self):
        w = []
        w.append(ADMIN_HANDLER_SEND_COMMAND)
        w.append(DEFAULT_PACKET_SIZE)
        w.append(NULL_BYTE)
        w.append(RESET_BASE_BOARD_COMMAND)

        size = self.write(w, TIMEOUT)

    def force_close_all(self):
        w = []
        w.append(ADMIN_HANDLER_SEND_COMMAND)
        w.append(DEFAULT_PACKET_SIZE)
        w.append(NULL_BYTE)
        w.append(CLOSEALL_BASE_BOARD_COMMAND)

        size = self.write(w, TIMEOUT)

        raw = self.read(CLOSEALL_BASE_BOARD_RESPONSE_PACKET_SIZE, TIMEOUT)

        return raw[4]

    def get_modules_list(self):
        if self.listi == []:
            self.get_listi()
        s = self.get_handler_size()
        for m in self.listi:
            if not(m in self.hotplug) and not(m == 'port'):
                print m

        for m in range(1, s+1):
            module_type = self.get_handler_type(m)
            module_name = self.listi[module_type]
            print module_name + ':' +  str(m)


    def get_listi(self):
        self.listi = []
        s = self.get_user_modules_size()
        for m in range(s):
            name = self.get_user_module_line(m)
            t = self.get_handler_type(m)
            self.listi.append(name)
            #print name  #, t
        return self.listi


    def module_send(self, handler, data):
        
        user_module_handler_send_command = handler * 8
        send_packet_length = 0x04

        w = []
        w.append(user_module_handler_send_command)
        w.append(send_packet_length)
        w.append(NULL_BYTE)
        w.append(data)

        size = self.write(w, TIMEOUT)

    def module_read(self, lenght):

        raw = self.read(READ_HEADER_SIZE  + lenght, TIMEOUT)

        l = []
        for i in range(READ_HEADER_SIZE, READ_HEADER_SIZE + lenght):
            l.append(raw[i])

        return l

    def module_open(self, module):
        w = []

        OPEN_COMMAND = 0x00
        CLOSE_COMMAND = 0x01
        HEADER_PACKET_SIZE = 0x06


        OPEN_RESPONSE_PACKET_SIZE = 5
        CLOSE_RESPONSE_PACKET_SIZE = 2

        module_name = self.to_ord(module)
        
        open_packet_length = HEADER_PACKET_SIZE + len(module_name) 

        module_in_endpoint  = 0x01
        module_out_endpoint = 0x01

        w.append(ADMIN_HANDLER_SEND_COMMAND)
        w.append(open_packet_length)
        w.append(NULL_BYTE)
        w.append(OPEN_COMMAND)
        w.append(module_in_endpoint)
        w.append(module_out_endpoint)
        w = w + module_name

        size = self.write(w, TIMEOUT)

        raw = self.read(OPEN_RESPONSE_PACKET_SIZE, TIMEOUT)

        return raw

    def to_ord(self, string):
        s = []
        for l in string:
            s.append(ord(l))

        # usb4all expect null terminated names
        s.append(0)
        
        return s


def find():
    # Get busses
    for bus in usb.busses():
        for dev in bus.devices:
            if dev.idVendor == USB4ALL_VENDOR and dev.idProduct == USB4ALL_PRODUCT:
                return USB4butia(dev)




