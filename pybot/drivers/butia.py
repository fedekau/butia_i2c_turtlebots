
RD_VERSION = 0x02
GET_VOLT = 0x03

f1 = {
    'name': 'getVersion',
    'call': RD_VERSION,
    'read': 2
}

f2 = {
    'name': 'get_volt',
    'call': GET_VOLT,
    'read': 2
}

FUNCTIONS = [f1, f2]
