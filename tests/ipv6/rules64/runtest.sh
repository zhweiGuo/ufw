#!/bin/bash

#    Copyright (C) 2008 Canonical Ltd.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License version 3,
#    as published by the Free Software Foundation.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

source "$TESTPATH/../testlib.sh"
sed -i 's/IPV6=no/IPV6=yes/' $TESTPATH/etc/default/ufw

echo "Man page" >> $TESTTMP/result
do_cmd "0" --dry-run allow 53
do_cmd "0" --dry-run allow 25/tcp
do_cmd "0" --dry-run allow smtp
do_cmd "0" --dry-run deny proto tcp to any port 80
do_cmd "0" --dry-run deny proto tcp from 10.0.0.0/8 to 192.168.0.1 port 25
do_cmd "0" --dry-run deny proto tcp from 2001:db8::/32 to any port 25
do_cmd "0" --dry-run allow 80/tcp
do_cmd "0" --dry-run delete allow 80/tcp
do_cmd "0" --dry-run deny 53
do_cmd "0" --dry-run allow 80/tcp
do_cmd "0" --dry-run allow from 10.0.0.0/8
do_cmd "0" --dry-run allow from 172.16.0.0/12
do_cmd "0" --dry-run allow from 192.168.0.0/16
do_cmd "0" --dry-run deny proto udp from 1.2.3.4 to any port 514
do_cmd "0" --dry-run allow proto udp from 1.2.3.5 port 5469 to 1.2.3.4 port 5469

echo "Services SIMPLE" >> $TESTTMP/result
do_cmd "0" --dry-run allow smtp
do_cmd "0" --dry-run delete allow smtp
do_cmd "0" --dry-run allow smtp/tcp
do_cmd "0" --dry-run delete allow smtp/tcp
do_cmd "0" --dry-run allow tftp
do_cmd "0" --dry-run delete allow tftp
do_cmd "0" --dry-run allow tftp/udp
do_cmd "0" --dry-run delete allow tftp/udp
do_cmd "0" --dry-run allow ssh
do_cmd "0" --dry-run delete allow ssh
do_cmd "0" --dry-run allow ssh/tcp
do_cmd "0" --dry-run delete allow ssh/tcp
do_cmd "0" --dry-run allow ssh/udp
do_cmd "0" --dry-run delete allow ssh/udp

echo "Services EXTENDED" >> $TESTTMP/result
do_cmd "0" --dry-run allow to any port smtp from any port ssh
do_cmd "0" --dry-run delete allow to any port smtp from any port ssh
do_cmd "0" --dry-run allow to any port tftp from any port ssh
do_cmd "0" --dry-run delete allow to any port tftp from any port ssh
do_cmd "0" --dry-run allow to any port ssh from any port domain
do_cmd "0" --dry-run delete allow to any port ssh from any port domain

echo "Netmasks" >> $TESTTMP/result
do_cmd "0" --dry-run allow to 192.168.0.0/0
do_cmd "0" --dry-run allow to 192.168.0.0/16
do_cmd "0" --dry-run allow to 192.168.0.1/32
do_cmd "0" --dry-run allow from 192.168.0.0/0
do_cmd "0" --dry-run allow from 192.168.0.0/16
do_cmd "0" --dry-run allow from 192.168.0.1/32
do_cmd "0" --dry-run allow from 192.168.0.1/32 to 192.168.0.2/32

do_cmd "0" --dry-run allow to ::1/0
do_cmd "0" --dry-run allow to ::1/32
do_cmd "0" --dry-run allow to ::1/128
do_cmd "0" --dry-run allow from ::1/0
do_cmd "0" --dry-run allow from ::1/32
do_cmd "0" --dry-run allow from ::1/128
do_cmd "0" --dry-run allow from ::1/32 to ::1/16

exit 0
