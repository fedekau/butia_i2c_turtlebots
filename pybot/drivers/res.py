
RD_VERSION = 0x00
GET_VALUE = 0x01

f1 = {
    'name': 'getVersion',
    'call': RD_VERSION,
    'read': 3
}

f2 = {
    'name': 'getValue',
    'call': GET_VALUE,
    'read': 3
}

FUNCTIONS = [f1, f2]
