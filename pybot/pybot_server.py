#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# pybot server
#

import socket
from threading import Thread
import usb4butia


PYBOT_HOST = 'localhost'
PYBOT_PORT = 2009


class Client(Thread):
    def __init__(self, socket, addr, robot):
        Thread.__init__(self)
        self.sc = socket
        self.addr = addr
        self.robot = robot

    def run(self):

        alive = True
        while alive:
            result = ''
            rec = self.sc.recv(1024)
            
            # remove end line characters if become from telnet
            r = rec.replace('\r', '')
            r = r.replace('\n', '')

            r = r.split(' ')
  
            print 'split', r

            if len(r) > 0:
                if r[0] == 'QUIT':
                    result = 'BYE'
                    alive = False

                elif r[0] == 'LIST':
                    l = self.robot.get_modules_list()
                    result = ','.join(l)

                elif r[0] == 'REFRESH':
                    self.robot.refresh()

                elif r[0] == 'BUTIA_COUNT':
                    result = self.robot.get_butia_count()

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
                        par = r[3:]
                        params = ' '.join(par)

                    result = self.call_aux(modulename, int(board), int(number), function, params)

                if not result == '':
                    result = str(result)
                print 'mando', result

                self.sc.send(result + '\n')

            else:
                print 'null message'
                self.sc.send('\n')
          
        print 'Closing...', self.addr
        self.sc.close()


    def call_aux(self, modulename, board_number, number, function, params):
        params = params.split(' ')
        print 'call aux', params
        par = []
        if modulename == 'motors':
            if function == 'setvel2mtr':
                if len(params) == 4:
                    return self.robot.set2MotorSpeed(int(params[0]), int(params[1]), int(params[2]), int(params[3]))
                elif len(params) == 6:
                    for e in params:
                        par.append(int(e))
                    return self.robot.callModule(modulename, board_number, number, function, par)
        else:
            return self.robot.callModule(modulename, board_number, number, function, par)


class Server():

    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((PYBOT_HOST, PYBOT_PORT))
        self.socket.listen(4)

        self.robot = usb4butia.USB4Butia()

    def init_server(self):

        self.sc, self.addr = self.socket.accept()

        print "conectado a "+ str(self.addr)

        t = Client(self.sc, self.addr, self.robot)
        t.start()

        #self.socket.close()
        #self.robot.close()


if __name__ == "__main__":
    s = Server()
    s.init_server()

