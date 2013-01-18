#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# pybot server
#

import socket
import usb4butia


PYBOT_HOST = 'localhost'
PYBOT_PORT = 2009

class server():

    def __init__(self):
        self.socket = socket.socket()
        self.socket.bind((PYBOT_HOST, PYBOT_PORT))
        self.socket.listen(1)
        

        self.robot = usb4butia.USB4Butia()

    def init_server(self):

        self.sc, self.addr = self.socket.accept()

        while True:  
            rec = self.sc.recv(1024)
            print "llego ", rec
            r = rec.split(' ')
            s = 'return:'
            print 'split', r

            if len(r) > 1:
                if r[0] == 'LIST':
                    l = self.robot.get_modules_list()
                    s = ", ".join(l)
                elif r[0] == 'CALL':
                    board = 0
                    number = 0
                    mbn = r[1]
                    if mbn.count('@') > 0:
                        modulename, bn = mbn.split('@')
                        board, number = bn.split(':')
                    else:
                        if mbn.count(':') > 0:
                            modulename, number = mbn.split(':')
                        else:
                            modulename = mbn
                    function = r[2]
                    print 'datos', modulename, board, number, function
                    params = ''
                    if len(r) > 3:
                        params = r[3]
                    resultado = self.robot.callModule(modulename, int(board), int(number), function, params)
                    s = s + 'salida: ' +  str(resultado)

            if rec == 'QUIT':  
                break
             
            self.sc.send(s)  
          
        print 'Closing..'  
          
        self.sc.close()  
        self.socket.close() 

if __name__ == "__main__":
    s = server()
    s.init_server()

