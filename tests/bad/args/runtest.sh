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

echo "TESTING ARGS (logging)" >> $TESTTMP/result
do_cmd "1" null --dry-run logging
do_cmd "1" null --dry-run logging foo
do_cmd "1" null --dry-run loggin on

echo "TESTING ARGS (default)" >> $TESTTMP/result
do_cmd "1" null --dry-run default
do_cmd "1" null --dry-run default foo
do_cmd "1" null --dry-run default accept
do_cmd "1" null --dry-run defaul allow
do_cmd "1" null --dry-run default limit

echo "TESTING ARGS (enable/disable)" >> $TESTTMP/result
# bad
do_cmd "1" null --dry-run enabled
do_cmd "1" null --dry-run disabled

echo "TESTING ARGS (allow/deny/limit)" >> $TESTTMP/result
do_cmd "1" null --dry-run allow
do_cmd "1" null --dry-run deny
do_cmd "1" null --dry-run limit

echo "TESTING ARGS (allow/deny/limit bad port)" >> $TESTTMP/result
do_cmd "1" null --dry-run alow 25
do_cmd "1" null --dry-run dny 25
do_cmd "1" null --dry-run limt 25
do_cmd "1" null --dry-run allow 25a
do_cmd "1" null --dry-run deny 25a
do_cmd "1" null --dry-run limit 25a
do_cmd "1" null --dry-run allow 65536
do_cmd "1" null --dry-run deny 65536
do_cmd "1" null --dry-run limit 65536
do_cmd "1" null --dry-run allow 0
do_cmd "1" null --dry-run deny 0
do_cmd "1" null --dry-run limit 0
do_cmd "1" null --dry-run deny XXX
do_cmd "1" null --dry-run deny foobar

echo "TESTING ARGS (allow/deny/limit bad to/from)" >> $TESTTMP/result
ip="192.168.0.1"
for action in allow deny limit
do
        do_cmd "1" null --dry-run $action prot tcp from any
        do_cmd "1" null --dry-run $action proto tcp fro any
        do_cmd "1" null --dry-run $action proto tcp top any
        do_cmd "1" null --dry-run $action proto tcp to any por 25

	do_cmd "1" null --dry-run $action port 25
	do_cmd "1" null --dry-run $action to anu
	do_cmd "1" null --dry-run $action proto tcq to any port 25
	do_cmd "1" null --dry-run $action proto tcp proto udp to any port 25

	do_cmd "1" null --dry-run $action to
	do_cmd "1" null --dry-run $action to port 25

	do_cmd "1" null --dry-run $action from
	do_cmd "1" null --dry-run $action from port 25

	do_cmd "1" null --dry-run $action to any port
	do_cmd "1" null --dry-run $action to port 25

	do_cmd "1" null --dry-run $action from $ip to
	do_cmd "1" null --dry-run $action from $ip from
	do_cmd "1" null --dry-run $action from $ip port 25 to
	do_cmd "1" null --dry-run $action from $ip port 25 from

	do_cmd "1" null --dry-run $action to $ip from
	do_cmd "1" null --dry-run $action to $ip to
	do_cmd "1" null --dry-run $action to $ip port smtp from
	do_cmd "1" null --dry-run $action to $ip port smtp to

	do_cmd "1" null --dry-run $action to from $ip
	do_cmd "1" null --dry-run $action from to $ip
	do_cmd "1" null --dry-run $action to from $ip port 25
	do_cmd "1" null --dry-run $action from to $ip port 25

	do_cmd "1" null --dry-run $action from from $ip
	do_cmd "1" null --dry-run $action to to $ip
	do_cmd "1" null --dry-run $action from from $ip port smtp
	do_cmd "1" null --dry-run $action to to $ip port smtp
done

echo "TESTING ARGS (bad ip)" >> $TESTTMP/result
do_cmd "1" null --dry-run allow to 192.168.0.
do_cmd "1" null --dry-run allow to 192.168.0.1.1
do_cmd "1" null --dry-run allow to foo
do_cmd "1" null --dry-run allow to xxx.xxx.xxx.xx
do_cmd "1" null --dry-run allow to 192a.168.0.1
do_cmd "1" null --dry-run allow to 192.168a.0.1
do_cmd "1" null --dry-run allow to 192.168.0a.1
do_cmd "1" null --dry-run allow to 192.168.1.a1
do_cmd "1" null --dry-run allow to 192.168.1..1
do_cmd "1" null --dry-run allow to 192.168.1..1/24
do_cmd "1" null --dry-run allow to 192.168.1.256
do_cmd "1" null --dry-run allow to 256.0.0.0
do_cmd "1" null --dry-run allow to 10.256.0.0

echo "TESTING ARGS (delete)" >> $TESTTMP/result
do_cmd "1" null --dry-run delete

echo "TESTING ARGS (allow/deny/limit mixed ipv4/ipv6)" >> $TESTTMP/result
do_cmd "1" null --dry-run allow to 10.0.0.1 from 2001:db8::/32
do_cmd "1" null --dry-run deny to 10.0.0.1 port 25 from 2001:db8::/32 proto tcp
do_cmd "1" null --dry-run limit to 10.0.0.1 port 25 from 2001:db8::/32 proto tcp
do_cmd "1" null --dry-run allow to 2001:db8::/32 port 25 from 10.0.0.1 proto udp
do_cmd "1" null --dry-run deny to 2001:db8::/32 from 10.0.0.1
do_cmd "1" null --dry-run limit to 2001:db8::/32 from 10.0.0.1

echo "TESTING ARGS (allow/deny/limit ipv6 when not enabled)" >> $TESTTMP/result
do_cmd "1" null --dry-run deny proto tcp from 2001:db8::/32 to any port 25
do_cmd "1" null --dry-run allow proto tcp from 2001:db8::/32 port 25 to any
do_cmd "1" null --dry-run limit proto tcp from 2001:db8::/32 port 25 to any
do_cmd "1" null --dry-run deny proto udp to 2001:db8::/32 from any port 25
do_cmd "1" null --dry-run allow proto udp to 2001:db8::/32 port 25 from any
do_cmd "1" null --dry-run limit proto udp to 2001:db8::/32 port 25 from any

echo "TESTING BAD SERVICES" >> $TESTTMP/result
do_cmd "1" null --dry-run allow smtp/udp
do_cmd "1" null --dry-run allow tftp/tcp
do_cmd "1" null --dry-run allow to any port smtp from any port tftp
do_cmd "1" null --dry-run allow to any port tftp from any port smtp
do_cmd "1" null --dry-run allow to any port smtp from any port 23 proto udp
do_cmd "1" null --dry-run allow to any port 23 from any port smtp proto udp
do_cmd "1" null --dry-run allow to any port tftp from any port 23 proto tcp
do_cmd "1" null --dry-run allow to any port 23 from any port tftp proto tcp
do_cmd "1" null --dry-run allow to any port smtp from any port ssh proto udp
do_cmd "1" null --dry-run allow to any port tftp from any port ssh proto tcp

exit 0
