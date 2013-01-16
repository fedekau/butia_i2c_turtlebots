
RD_VERSION = 0x00

f1 = {
    'name': 'getVersion',
    'call': RD_VERSION,
    'params': 0,
    'read': 3
}

f2 = {
    'name': 'send',
    'params': 1
}

f3 = {
    'name': 'read',
    'params': 0
}

FUNCTIONS = [f1, f2, f3]
