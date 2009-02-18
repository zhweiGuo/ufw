#!/bin/bash

#    Copyright (C) 2008-2009 Canonical Ltd.
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

for ipv6 in yes no
do
	echo "Setting IPV6 to $ipv6" >> $TESTTMP/result
	sed -i "s/IPV6=.*/IPV6=$ipv6/" $TESTPATH/etc/default/ufw
	do_cmd "0"  disable 
	do_cmd "0"  enable 

	echo "TESTING ARGS (logging)" >> $TESTTMP/result
	do_cmd "0"  logging on 
	grep -h "LOG" $TESTPATH/etc/ufw/*.rules >> $TESTTMP/result
	do_cmd "0"  logging off 
	grep -h "LOG" $TESTPATH/etc/ufw/*.rules >> $TESTTMP/result

	echo "TESTING ARGS (allow/deny to/from)" >> $TESTTMP/result
	do_cmd "0" allow 53
	do_cmd "0" allow 23/tcp
	do_cmd "0" allow smtp
	do_cmd "0" deny proto tcp to any port 80
	do_cmd "0" deny proto tcp from 10.0.0.0/8 to 192.168.0.1 port 25
	do_cmd "0" allow from 10.0.0.0/8
	do_cmd "0" allow from 172.16.0.0/12
	do_cmd "0" allow from 192.168.0.0/16
	do_cmd "0" deny proto udp from 1.2.3.4 to any port 514
	do_cmd "0" allow proto udp from 1.2.3.5 port 5469 to 1.2.3.4 port 5469
	do_cmd "0" limit 22/tcp
	if [ "$ipv6" = "yes" ]; then
		do_cmd "0" deny proto tcp from 2001:db8::/32 to any port 25
		do_cmd "0" deny from 2001:db8::/32 port 26 to 2001:db8:3:4:5:6:7:8
	fi
	do_cmd "0" status
	grep -A2 "tuple" $TESTPATH/var/lib/ufw/user.rules >> $TESTTMP/result
	grep -A2 "tuple" $TESTPATH/var/lib/ufw/user6.rules >> $TESTTMP/result

	echo "TESTING ARGS (delete allow/deny to/from)" >> $TESTTMP/result
	do_cmd "0" delete allow 53
	do_cmd "0" delete allow 23/tcp
	do_cmd "0" delete allow smtp
	do_cmd "0" delete deny proto tcp to any port 80
	do_cmd "0" delete deny proto tcp from 10.0.0.0/8 to 192.168.0.1 port 25
	do_cmd "0" delete allow from 10.0.0.0/8
	do_cmd "0" delete allow from 172.16.0.0/12
	do_cmd "0" delete allow from 192.168.0.0/16
	do_cmd "0" delete deny proto udp from 1.2.3.4 to any port 514
	do_cmd "0" delete allow proto udp from 1.2.3.5 port 5469 to 1.2.3.4 port 5469
	do_cmd "0" delete limit 22/tcp
	if [ "$ipv6" = "yes" ]; then
		do_cmd "0" delete deny proto tcp from 2001:db8::/32 to any port 25
		do_cmd "0" delete deny from 2001:db8::/32 port 26 to 2001:db8:3:4:5:6:7:8
	fi
	do_cmd "0" status
	grep -A2 "tuple" $TESTPATH/var/lib/ufw/user.rules >> $TESTTMP/result
	grep -A2 "tuple" $TESTPATH/var/lib/ufw/user6.rules >> $TESTTMP/result
done


echo "Checking status" >> $TESTTMP/result
do_cmd "0" null status
do_cmd "0" null status verbose
do_cmd "0" null status raw

echo "Checking reject" >> $TESTTMP/result
for ipv6 in yes no
do
	echo "Setting IPV6 to $ipv6" >> $TESTTMP/result
	sed -i "s/IPV6=.*/IPV6=$ipv6/" $TESTPATH/etc/default/ufw
	do_cmd "0" disable
	do_cmd "0" enable
	do_cmd "0" reject 113
	do_cmd "0" reject 114/tcp
	do_cmd "0" reject 115/udp
	do_cmd "0" status
	grep -A2 "tuple" $TESTPATH/var/lib/ufw/user.rules >> $TESTTMP/result
	grep -A2 "tuple" $TESTPATH/var/lib/ufw/user6.rules >> $TESTTMP/result
	do_cmd "0" delete reject 113
	do_cmd "0" delete reject 114/tcp
	do_cmd "0" delete reject 115/udp
	do_cmd "0" status
	grep -A2 "tuple" $TESTPATH/var/lib/ufw/user.rules >> $TESTTMP/result
	grep -A2 "tuple" $TESTPATH/var/lib/ufw/user6.rules >> $TESTTMP/result
done

echo "Checking flush builtins" >> $TESTTMP/result
for ans in yes no
do
        str="ufw_test_builtins"
        do_cmd "0"  disable
        sed -i "s/MANAGE_BUILTINS=.*/MANAGE_BUILTINS=$ans/" $TESTPATH/etc/default/ufw

        iptables -D INPUT -j ACCEPT -m comment --comment $str 2>/dev/null
        echo iptables -I INPUT -j ACCEPT -m comment --comment $str >> $TESTTMP/result
        iptables -I INPUT -j ACCEPT -m comment --comment $str >> $TESTTMP/result
        do_cmd "0" enable
        iptables -n -L INPUT | grep "$str" >> $TESTTMP/result
done

echo "Testing status numbered" >> $TESTTMP/result
for ipv6 in yes no
do
	echo "Setting IPV6 to $ipv6" >> $TESTTMP/result
	sed -i "s/IPV6=.*/IPV6=$ipv6/" $TESTPATH/etc/default/ufw
	do_cmd "0"  disable 
	do_cmd "0"  enable 

	do_cmd "0" allow 53
	do_cmd "0" allow 23/tcp
	do_cmd "0" allow smtp
	do_cmd "0" deny proto tcp to any port 80
	do_cmd "0" deny proto tcp from 10.0.0.0/8 to 192.168.0.1 port 25
	do_cmd "0" allow from 10.0.0.0/8
	do_cmd "0" allow from 172.16.0.0/12
	do_cmd "0" allow from 192.168.0.0/16
	do_cmd "0" deny proto udp from 1.2.3.4 to any port 514
	do_cmd "0" allow proto udp from 1.2.3.5 port 5469 to 1.2.3.4 port 5469
	do_cmd "0" limit 22/tcp
	if [ "$ipv6" = "yes" ]; then
		do_cmd "0" deny proto tcp from 2001:db8::/32 to any port 25
		do_cmd "0" deny from 2001:db8::/32 port 26 to 2001:db8:3:4:5:6:7:8
	fi
	do_cmd "0" status numbered

	do_cmd "0" delete allow 53
	do_cmd "0" delete allow 23/tcp
	do_cmd "0" delete allow smtp
	do_cmd "0" delete deny proto tcp to any port 80
	do_cmd "0" delete deny proto tcp from 10.0.0.0/8 to 192.168.0.1 port 25
	do_cmd "0" delete allow from 10.0.0.0/8
	do_cmd "0" delete allow from 172.16.0.0/12
	do_cmd "0" delete allow from 192.168.0.0/16
	do_cmd "0" delete deny proto udp from 1.2.3.4 to any port 514
	do_cmd "0" delete allow proto udp from 1.2.3.5 port 5469 to 1.2.3.4 port 5469
	do_cmd "0" delete limit 22/tcp
	if [ "$ipv6" = "yes" ]; then
		do_cmd "0" delete deny proto tcp from 2001:db8::/32 to any port 25
		do_cmd "0" delete deny from 2001:db8::/32 port 26 to 2001:db8:3:4:5:6:7:8
	fi
	do_cmd "0" status numbered
done

cleanup

exit 0
