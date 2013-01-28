
RD_VERSION = 0x00
SET_27_TO_30 = 0x01 # opcode to set 4pin values
SET_PIN27 = 0x02 # opcode to set individual values
SET_PIN28 = 0x03
SET_PIN29 = 0x04
SET_PIN30 = 0x05
GET_PIN27 = 0x06 #opcode to get pin values
GET_PIN28 = 0x07
GET_PIN29 = 0x08
GET_PIN30 = 0x09

f1 = {
    'name': 'getVersion',
    'call': RD_VERSION,
    'params': 0,
    'read': 3
}

f2 = {
    'name': 'set4pin',
    'call': SET_27_TO_30,
    'params': 4,
    'read': 1
}

FUNCTIONS = [f1, f2]
