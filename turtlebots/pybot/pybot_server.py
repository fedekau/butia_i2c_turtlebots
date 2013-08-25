#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Pybot server
#
# Copyright (c) 2012-2013 Butiá Team butia@fing.edu.uy 
# Butia is a free and open robotic platform
# www.fing.edu.uy/inco/proyectos/butia
# Facultad de Ingeniería - Universidad de la República - Uruguay
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import sys
import select
import socket
import usb4butia
import com_chotox

argv = sys.argv[:]

PYBOT_PORT = 2009
BUFSIZ = 1024
MAX_CLIENTS = 4


class Server():

    def __init__(self, debug=False, chotox=False):
        self.debug = debug
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(("", PYBOT_PORT))
        self.socket.listen(MAX_CLIENTS)
        self.clients = {}
        self.chotox_mode = chotox
        if self.chotox_mode:
            self.robot = com_chotox.Chotox(debug=self.debug)
        else:
            self.robot = usb4butia.USB4Butia(debug=self.debug)

    def init_server(self):

        inputs = [self.socket]

        run = True
        while run:

            try:
                inputready,outputready,exceptready = select.select(inputs, [], [])
            except Exception, err:
                print 'Error in select', err
                break

            for s in inputready:
                if s == self.socket:
                    client, addr = self.socket.accept()
                    print 'New client: ', str(addr)
                    inputs.append(client)
                    self.clients[client] = addr
                else:
                    data = s.recv(BUFSIZ)
                    if data:
                        result = ''
                        # remove end line characters if become from telnet
                        r = data.replace('\r', '')
                        r = r.replace('\n', '')
                        r = r.split(' ')

                        if len(r) > 0:
                            if r[0] == 'QUIT':
                                result = 'BYE'
                                run = False
                            elif r[0] == 'CLIENTS':
                                first = True
                                for c in self.clients:
                                    addr = self.clients[c]
                                    if first:
                                        result = result + str(addr[0]) + ', ' + str(addr[1]) 
                                        first = False
                                    else:
                                        result = result + '\n' + str(addr[0]) + ', ' + str(addr[1]) 
                            elif r[0] == 'LIST':
                                l = self.robot.getModulesList()
                                result = ','.join(l)
                            elif r[0] == 'LISTI':
                                board = 0
                                if len(r) >= 2:
                                    board = r[1]
                                l = self.robot.getListi(board)
                                result = ','.join(l)
                            elif r[0] == 'REFRESH':
                                self.robot.refresh()
                            elif r[0] == 'BUTIA_COUNT':
                                result = self.robot.getButiaCount()
                            elif r[0] == 'DESCRIBE':
                                if len(r) >= 2:
                                    module = r[1]
                                    funcs = self.robot.describe(module)
                                    result = ','.join(funcs)
                            elif r[0] == 'OPEN':
                                if len(r) >= 2:
                                    module = r[1]
                                    result = self.robot.module_open(module)
                            elif r[0] == 'CLOSE':
                                if len(r) >= 2:
                                    module = r[1]
                                    result = self.robot.module_close(module)
                            elif r[0] == 'CALL':
                                if len(r) >= 3:
                                    split = self.robot._split_module(r[1])
                                    result = self.robot.callModule(split[1], split[2], split[0], r[2], r[3:])

                        result = str(result)
                        try:
                            s.send(result + '\n')
                        except:
                            print 'Send fails'

                    else:
                        s.close()
                        inputs.remove(s)
                        self.clients.pop(s)
                        
        print 'Closing server'
        self.socket.close()
        self.robot.close()


if __name__ == "__main__":
    chotox = 'chotox' in argv
    debug = 'DEBUG' in argv
    s = Server(debug, chotox)
    s.init_server()

