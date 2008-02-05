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

echo "TESTING ARGS (logging)" >> $TESTTMP/result
do_cmd "0"  logging on 
grep -h "LOG" $TESTPATH/etc/ufw/*.rules >> $TESTTMP/result
do_cmd "0"  logging off 
grep -h "LOG" $TESTPATH/etc/ufw/*.rules >> $TESTTMP/result
do_cmd "0"  LOGGING ON 
grep -h "LOG" $TESTPATH/etc/ufw/*.rules >> $TESTTMP/result
do_cmd "0"  LOGGING OFF 
grep -h "LOG" $TESTPATH/etc/ufw/*.rules >> $TESTTMP/result

echo "TESTING ARGS (default)" >> $TESTTMP/result
do_cmd "0"  enable 
do_cmd "0"  default allow
echo "ipv4:" >> $TESTTMP/result
iptables -L -n | grep policy >> $TESTTMP/result
echo "ipv6:" >> $TESTTMP/result
ip6tables -L -n | grep policy >> $TESTTMP/result
grep -h "DEFAULT" $TESTPATH/etc/default/ufw >> $TESTTMP/result
do_cmd "0"  default deny
echo "ipv4:" >> $TESTTMP/result
iptables -L -n | grep policy >> $TESTTMP/result
echo "ipv6:" >> $TESTTMP/result
ip6tables -L -n | grep policy >> $TESTTMP/result
grep -h "DEFAULT" $TESTPATH/etc/default/ufw >> $TESTTMP/result
do_cmd "0"  DEFAULT ALLOW
echo "ipv4:" >> $TESTTMP/result
iptables -L -n | grep policy >> $TESTTMP/result
echo "ipv6:" >> $TESTTMP/result
ip6tables -L -n | grep policy >> $TESTTMP/result
grep -h "DEFAULT" $TESTPATH/etc/default/ufw >> $TESTTMP/result
do_cmd "0"  DEFAULT DENY
echo "ipv4:" >> $TESTTMP/result
iptables -L -n | grep policy >> $TESTTMP/result
echo "ipv6:" >> $TESTTMP/result
ip6tables -L -n | grep policy >> $TESTTMP/result
grep -h "DEFAULT" $TESTPATH/etc/default/ufw >> $TESTTMP/result

do_cmd "0"  default deny
do_cmd "0"  disable 

echo "TESTING ARGS (enable/disable)" >> $TESTTMP/result
do_cmd "0"  enable 
cat $TESTPATH/etc/default/ufw | egrep '^ENABLED' >> $TESTTMP/result
do_cmd "0"  disable 
cat $TESTPATH/etc/default/ufw | egrep '^ENABLED' >> $TESTTMP/result
do_cmd "0"  ENABLE 
cat $TESTPATH/etc/default/ufw | egrep '^ENABLED' >> $TESTTMP/result
do_cmd "0"  DISABLE 
cat $TESTPATH/etc/default/ufw | egrep '^ENABLED' >> $TESTTMP/result

echo "TESTING ARGS (allow/deny to/from)" >> $TESTTMP/result
echo "Man page" >> $TESTTMP/result
do_cmd "0" deny proto tcp from 2001:db8::/32 to any port 25
grep -A2 "tuple" $TESTPATH/var/lib/ufw/user6.rules >> $TESTTMP/result

do_cmd "0"  delete deny proto tcp from 2001:db8::/32 to any port 25
grep -A2 "tuple" $TESTPATH/var/lib/ufw/user6.rules >> $TESTTMP/result


echo "TO/FROM" >> $TESTTMP/result
from="2001:db8::/32"
to="2001:db8:3:4:5:6:7:8"
for x in allow deny
do
        do_cmd "0"  $x from $from
	grep -A2 "tuple" $TESTPATH/var/lib/ufw/user6.rules >> $TESTTMP/result
        do_cmd "0"  delete $x from $from
	grep -A2 "tuple" $TESTPATH/var/lib/ufw/user6.rules >> $TESTTMP/result
        do_cmd "0"  $x to $to
	grep -A2 "tuple" $TESTPATH/var/lib/ufw/user6.rules >> $TESTTMP/result
        do_cmd "0"  delete $x to $to
	grep -A2 "tuple" $TESTPATH/var/lib/ufw/user6.rules >> $TESTTMP/result
        do_cmd "0"  $x to $to from $from
	grep -A2 "tuple" $TESTPATH/var/lib/ufw/user6.rules >> $TESTTMP/result
        do_cmd "0"  delete $x to $to from $from
	grep -A2 "tuple" $TESTPATH/var/lib/ufw/user6.rules >> $TESTTMP/result

        do_cmd "0"  $x from $from port 80
	grep -A2 "tuple" $TESTPATH/var/lib/ufw/user6.rules >> $TESTTMP/result
        do_cmd "0"  delete $x from $from port 80
	grep -A2 "tuple" $TESTPATH/var/lib/ufw/user6.rules >> $TESTTMP/result
        do_cmd "0"  $x to $to port 25
	grep -A2 "tuple" $TESTPATH/var/lib/ufw/user6.rules >> $TESTTMP/result
        do_cmd "0"  delete $x to $to port 25
	grep -A2 "tuple" $TESTPATH/var/lib/ufw/user6.rules >> $TESTTMP/result
        do_cmd "0"  $x to $to from $from port 80
	grep -A2 "tuple" $TESTPATH/var/lib/ufw/user6.rules >> $TESTTMP/result
        do_cmd "0"  delete $x to $to from $from port 80
	grep -A2 "tuple" $TESTPATH/var/lib/ufw/user6.rules >> $TESTTMP/result
        do_cmd "0"  $x to $to port 25 from $from
	grep -A2 "tuple" $TESTPATH/var/lib/ufw/user6.rules >> $TESTTMP/result
        do_cmd "0"  delete $x to $to port 25 from $from
	grep -A2 "tuple" $TESTPATH/var/lib/ufw/user6.rules >> $TESTTMP/result
        do_cmd "0"  $x to $to port 25 from $from port 80
	grep -A2 "tuple" $TESTPATH/var/lib/ufw/user6.rules >> $TESTTMP/result
        do_cmd "0"  delete $x to $to port 25 from $from port 80
	grep -A2 "tuple" $TESTPATH/var/lib/ufw/user6.rules >> $TESTTMP/result
        for y in udp tcp
        do
                do_cmd "0"  $x from $from port 80 proto $y
		grep -A2 "tuple" $TESTPATH/var/lib/ufw/user6.rules >> $TESTTMP/result
                do_cmd "0"  delete $x from $from port 80 proto $y
		grep -A2 "tuple" $TESTPATH/var/lib/ufw/user6.rules >> $TESTTMP/result
                do_cmd "0"  $x to $to port 25 proto $y
		grep -A2 "tuple" $TESTPATH/var/lib/ufw/user6.rules >> $TESTTMP/result
                do_cmd "0"  delete $x to $to port 25 proto $y
		grep -A2 "tuple" $TESTPATH/var/lib/ufw/user6.rules >> $TESTTMP/result
                do_cmd "0"  $x to $to from $from port 80 proto $y
		grep -A2 "tuple" $TESTPATH/var/lib/ufw/user6.rules >> $TESTTMP/result
                do_cmd "0"  delete $x to $to from $from port 80 proto $y
		grep -A2 "tuple" $TESTPATH/var/lib/ufw/user6.rules >> $TESTTMP/result
                do_cmd "0"  $x to $to port 25 proto $y from $from
		grep -A2 "tuple" $TESTPATH/var/lib/ufw/user6.rules >> $TESTTMP/result
                do_cmd "0"  delete $x to $to port 25 proto $y from $from
		grep -A2 "tuple" $TESTPATH/var/lib/ufw/user6.rules >> $TESTTMP/result
                do_cmd "0"  $x to $to port 25 proto $y from $from port 80
		grep -A2 "tuple" $TESTPATH/var/lib/ufw/user6.rules >> $TESTTMP/result
                do_cmd "0"  delete $x to $to port 25 proto $y from $from port 80
		grep -A2 "tuple" $TESTPATH/var/lib/ufw/user6.rules >> $TESTTMP/result
        done
done

exit 0
