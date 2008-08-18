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

echo "Man page" >> $TESTTMP/result
do_cmd "0" --dry-run allow 53
do_cmd "0" --dry-run allow 25/tcp
do_cmd "0" --dry-run allow smtp
do_cmd "0" --dry-run deny proto tcp to any port 80
do_cmd "0" --dry-run deny proto tcp from 10.0.0.0/8 to 192.168.0.1 port 25
do_cmd "0" --dry-run deny 80/tcp
do_cmd "0" --dry-run delete deny 80/tcp
do_cmd "0" --dry-run limit ssh/tcp
do_cmd "0" --dry-run deny 53
do_cmd "0" --dry-run allow 80/tcp
do_cmd "0" --dry-run allow from 10.0.0.0/8
do_cmd "0" --dry-run allow from 172.16.0.0/12
do_cmd "0" --dry-run allow from 192.168.0.0/16
do_cmd "0" --dry-run deny proto udp from 1.2.3.4 to any port 514
do_cmd "0" --dry-run allow proto udp from 1.2.3.5 port 5469 to 1.2.3.4 port 5469

echo "SIMPLE" >> $TESTTMP/result
do_cmd "0" --dry-run allow 1
do_cmd "0" --dry-run allow 9/udp
do_cmd "0" --dry-run allow 25
do_cmd "0" --dry-run allow 25/tcp
do_cmd "0" --dry-run allow 25/udp
do_cmd "0" --dry-run delete allow 25
do_cmd "0" --dry-run delete allow 25/tcp
do_cmd "0" --dry-run delete allow 25/udp
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

echo "TO/FROM" >> $TESTTMP/result
from="192.168.0.1"
to="10.0.0.1"
for x in allow deny limit
do
	do_cmd "0" --dry-run $x from $from
	do_cmd "0" --dry-run delete $x from $from
	do_cmd "0" --dry-run $x to $to
	do_cmd "0" --dry-run delete $x to $to
	do_cmd "0" --dry-run $x to $to from $from
	do_cmd "0" --dry-run delete $x to $to from $from

	do_cmd "0" --dry-run $x from $from port 80
	do_cmd "0" --dry-run delete $x from $from port 80
	do_cmd "0" --dry-run $x to $to port 25
	do_cmd "0" --dry-run delete $x to $to port 25
	do_cmd "0" --dry-run $x to $to from $from port 80
	do_cmd "0" --dry-run delete $x to $to from $from port 80
	do_cmd "0" --dry-run $x to $to port 25 from $from
	do_cmd "0" --dry-run delete $x to $to port 25 from $from
	do_cmd "0" --dry-run $x to $to port 25 from $from port 80
	do_cmd "0" --dry-run delete $x to $to port 25 from $from port 80

	for y in udp tcp
	do
		do_cmd "0" --dry-run $x from $from port 80 proto $y
		do_cmd "0" --dry-run delete $x from $from port 80 proto $y
		do_cmd "0" --dry-run $x to $to port 25 proto $y
		do_cmd "0" --dry-run delete $x to $to port 25 proto $y
		do_cmd "0" --dry-run $x to $to from $from port 80 proto $y 
		do_cmd "0" --dry-run delete $x to $to from $from port 80 proto $y 
		do_cmd "0" --dry-run $x to $to port 25 proto $y from $from
		do_cmd "0" --dry-run delete $x to $to port 25 proto $y from $from
		do_cmd "0" --dry-run $x to $to port 25 proto $y from $from port 80
		do_cmd "0" --dry-run delete $x to $to port 25 proto $y from $from port 80
	done
done

echo "Services" >> $TESTTMP/result
do_cmd "0" --dry-run allow to any port smtp from any port smtp
do_cmd "0" --dry-run delete allow to any port smtp from any port smtp
do_cmd "0" --dry-run allow to any port smtp from any port ssh
do_cmd "0" --dry-run delete allow to any port smtp from any port ssh
do_cmd "0" --dry-run allow to any port ssh from any port smtp
do_cmd "0" --dry-run delete allow to any port ssh from any port smtp
do_cmd "0" --dry-run allow to any port smtp from any port 23
do_cmd "0" --dry-run delete allow to any port smtp from any port 23
do_cmd "0" --dry-run allow to any port 23 from any port smtp
do_cmd "0" --dry-run delete allow to any port 23 from any port smtp
do_cmd "0" --dry-run allow to any port tftp from any port tftp
do_cmd "0" --dry-run delete allow to any port tftp from any port tftp
do_cmd "0" --dry-run allow to any port tftp from any port ssh
do_cmd "0" --dry-run delete allow to any port tftp from any port ssh
do_cmd "0" --dry-run allow to any port ssh from any port tftp
do_cmd "0" --dry-run delete allow to any port ssh from any port tftp
do_cmd "0" --dry-run allow to any port tftp from any port 23
do_cmd "0" --dry-run delete allow to any port tftp from any port 23
do_cmd "0" --dry-run allow to any port 23 from any port tftp
do_cmd "0" --dry-run delete allow to any port 23 from any port tftp
do_cmd "0" --dry-run allow to any port ssh from any port 23
do_cmd "0" --dry-run delete allow to any port ssh from any port 23
do_cmd "0" --dry-run allow to any port 23 from any port ssh
do_cmd "0" --dry-run delete allow to any port 23 from any port ssh
do_cmd "0" --dry-run allow to any port ssh from any port domain
do_cmd "0" --dry-run delete allow to any port ssh from any port domain

do_cmd "0" --dry-run allow to any port smtp from any port smtp proto tcp
do_cmd "0" --dry-run delete allow to any port smtp from any port smtp proto tcp
do_cmd "0" --dry-run allow to any port smtp from any port ssh proto tcp
do_cmd "0" --dry-run delete allow to any port smtp from any port ssh proto tcp
do_cmd "0" --dry-run allow to any port ssh from any port smtp proto tcp
do_cmd "0" --dry-run delete allow to any port ssh from any port smtp proto tcp
do_cmd "0" --dry-run allow to any port smtp from any port 23 proto tcp
do_cmd "0" --dry-run delete allow to any port smtp from any port 23 proto tcp
do_cmd "0" --dry-run allow to any port 23 from any port smtp proto tcp
do_cmd "0" --dry-run delete allow to any port 23 from any port smtp proto tcp
do_cmd "0" --dry-run allow to any port tftp from any port tftp proto udp
do_cmd "0" --dry-run delete allow to any port tftp from any port tftp proto udp
do_cmd "0" --dry-run allow to any port tftp from any port ssh proto udp
do_cmd "0" --dry-run delete allow to any port tftp from any port ssh proto udp
do_cmd "0" --dry-run allow to any port ssh from any port tftp proto udp
do_cmd "0" --dry-run delete allow to any port ssh from any port tftp proto udp
do_cmd "0" --dry-run allow to any port tftp from any port 23 proto udp
do_cmd "0" --dry-run delete allow to any port tftp from any port 23 proto udp
do_cmd "0" --dry-run allow to any port 23 from any port tftp proto udp
do_cmd "0" --dry-run delete allow to any port 23 from any port tftp proto udp
do_cmd "0" --dry-run allow to any port ssh from any port 23 proto tcp
do_cmd "0" --dry-run delete allow to any port ssh from any port 23 proto tcp
do_cmd "0" --dry-run allow to any port 23 from any port ssh proto tcp
do_cmd "0" --dry-run delete allow to any port 23 from any port ssh proto tcp
do_cmd "0" --dry-run allow to any port ssh from any port domain proto tcp
do_cmd "0" --dry-run delete allow to any port ssh from any port domain proto tcp
do_cmd "0" --dry-run allow to any port ssh from any port 23 proto udp
do_cmd "0" --dry-run delete allow to any port ssh from any port 23 proto udp
do_cmd "0" --dry-run allow to any port 23 from any port ssh proto udp
do_cmd "0" --dry-run delete allow to any port 23 from any port ssh proto udp
do_cmd "0" --dry-run allow to any port ssh from any port domain proto udp
do_cmd "0" --dry-run delete allow to any port ssh from any port domain proto udp

echo "Netmasks" >> $TESTTMP/result
do_cmd "0" --dry-run allow to 192.168.0.0/0
do_cmd "0" --dry-run allow to 192.168.0.0/16
do_cmd "0" --dry-run allow to 192.168.0.1/32
do_cmd "0" --dry-run allow from 192.168.0.0/0
do_cmd "0" --dry-run allow from 192.168.0.0/16
do_cmd "0" --dry-run allow from 192.168.0.1/32
do_cmd "0" --dry-run allow from 192.168.0.1/32 to 192.168.0.2/32

echo "ISP style" >> $TESTTMP/result
do_cmd "0" --dry-run allow from 192.168.0.2/255.255.0.2

echo "Multiports:" >> $TESTTMP/result
for i in 192.168.0 any; do
    for j in from to; do
        k="to"
        if [ "$j" = "to" ]; then
            k="from"
        fi
        m="$i.1"
        n="$i.2"
        if [ "$i" = "any" ]; then
            m="$i"
            n="$i"
        fi
        do_cmd "0" --dry-run allow $j $m port 34,35 proto tcp
        do_cmd "0" --dry-run allow $j $m port 34,35:39 proto udp
        do_cmd "0" --dry-run allow $j $m port 35:39 proto tcp
        do_cmd "0" --dry-run allow $j $m port 221,23,21,15:19,22 proto udp
        do_cmd "0" --dry-run allow $j $m port 34,35 $k $n port 24 proto tcp
        do_cmd "0" --dry-run allow $j $m port 34,35:39 $k $n port 24 proto udp
        do_cmd "0" --dry-run allow $j $m port 35:39 $k $n port 24 proto tcp
        do_cmd "0" --dry-run allow $j $m port 23,21,15:19,22 $k $n port 24 proto udp
        do_cmd "0" --dry-run allow $j $m port 34,35 $k $n port 24:26 proto tcp
        do_cmd "0" --dry-run allow $j $m port 34,35:39 $k $n port 24:26 proto udp
        do_cmd "0" --dry-run allow $j $m port 35:39 $k $n port 24:26 proto tcp
        do_cmd "0" --dry-run allow $j $m port 23,21,15:19,22 $k $n port 24:26 proto udp
    done
done

# simple syntax
for i in allow deny limit; do
    for j in tcp udp; do
	do_cmd "0" --dry-run $i 34,35/$j
	do_cmd "0" --dry-run $i 34,35:39/$j
	do_cmd "0" --dry-run $i 35:39/$j
	do_cmd "0" --dry-run $i 23,21,15:19,22/$j
	do_cmd "0" --dry-run $i 1,9/$j
    done
done

exit 0
