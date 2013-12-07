#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Pybot server functions
#
# Copyright (c) 2012-2013 Alan Aguiar alanjas@hotmail.com
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


def QUIT(parent, r):
    parent.run = False
    return 'BYE'

def REFRESH(parent, r):
    parent.robot.refresh()
    return ''

def OPEN(parent, r):
    if len(r) == 1:
        module = r[0]
        return parent.robot.moduleOpen(module)
    return ''

def CLOSE(parent, r):
    if len(r) == 1:
        module = r[0]
        return parent.robot.moduleClose(module)
    return ''

def DESCRIBE(parent, r):
    if len(r) == 1:
        module = r[0]
        return parent.robot.describe(module)
    return ''

def BUTIA_COUNT(parent, r):
    return parent.robot.getButiaCount()

def LISTI(parent, r):
    board = 0
    if len(r) >= 1:
        board = r[0]
    l = parent.robot.getListi(board)
    return ','.join(l)

def LIST(parent, r):
    l = parent.robot.getModulesList()
    return ','.join(l)

def CLIENTS(parent, r):
    l = []
    for c in parent.clients:
        addr = parent.clients[c]
        l.append(str(addr[0]) + ', ' + str(addr[1]))
    return '\n'.join(l)

def CALL(parent, r):
    if len(r) >= 2:
        split = parent.robot._split_module(r[0])
        return parent.robot.callModule(split[1], split[2], split[0], r[1], r[2:])
    return ''

def HELP(parent, r):
    l = []
    flag = True
    a = dir(parent.comms)
    if '__builtins__' in a:
        i = a.index('__builtins__')
        l = a[:i]
    return ', '.join(l)

