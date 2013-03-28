#!/bin/bash
# this file install permissions for users
#
# Copyright (C) 2012 Guillermo Reisch (greisch@fing.edu.uy)
#
# Butia is a free open plataform for robotics projects
# http://www.fing.edu.uy/inco/proyectos/butia
# Universidad de la República del Uruguay
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

if [ "`id -u`" != "0" ] ; then
    echo "YOU NEED TO BE ROOT!!!!"
    exit 1
fi 

if [ -e /etc/group ] ; then 
    # check if not exist lego group (create it if not...)
    if [ "x`cat /etc/group | grep ^robots:`" = "x" ] ; then 
         addgroup --system robots
    fi
    lusers=`cat /etc/passwd | grep "1[0-9]\{3\}" | sed "s/:.\+//"`
    echo "##########################################"
    echo "######### INSTALL PERMISSIONS  ###########"
    echo "##########################################"
    echo ""
    echo "This part set what users are in group 'robots'"
    echo "the group 'robots' allow users to use the robots: lego nxt,"
    echo "lego wedo and butia."
    echo "This script has detect the follow users in this machine:"
    echo "$lusers"
    echo ""
    echo "if this is correct just press ENTER"
    echo "if NOT correct you should write the users in the next line"
    echo -n "Users to include? [LIST/ENTER] : "
    read -t 10 tmpread
    if [ "x$tmpread" != "x" ] ; then 
         lusers=$tmpread;
    fi
    echo $lusers
    for i in $lusers ; do
	    adduser $i robots
    done
    udevadm control --reload-rules
fi ;
	

