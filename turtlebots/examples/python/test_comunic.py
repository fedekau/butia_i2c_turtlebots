#! /usr/bin/env python
# -*- coding: utf-8 -*-
# test de comunicacion

import socket

s = socket.socket()  
s.connect(("localhost", 2009))  
    
while True:  
    mensaje = raw_input("> ")  
    s.send(mensaje)  
    ret = s.recv(1024)
    ret = ret.replace('\n', '')
    print ret
    if mensaje == "QUIT":  
        break  
    
print "adios"  
s.close()
