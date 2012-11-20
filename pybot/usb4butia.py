
import usb


# Constantes



# Otras

#CONSTANTS



# BUTIA
RD_VERSION = 0x02
GET_VOLT = 0x03

#################################################



class USB4butia():

        self.listi = []
        self.hotplug = ['button', 'distanc', 'grey', 'light', 'volt', 'res']



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










