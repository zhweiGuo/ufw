#!/bin/bash

#    Copyright 2010 Canonical Ltd.
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

exit 0

echo "show listening" >> $TESTTMP/result
echo "(update util.py to use our cached output)" >> $TESTTMP/result
sed -i "s#rc, report = cmd.* '-enlp'.*#rc, report = cmd(['cat', '$TESTPATH/../good/reports/netstat.enlp'])#" $TESTPATH/lib/python/ufw/util.py
sed -i "s#item\['exe'\] = get_exe.*#item['exe'] = 'REMOVED_FOR_UFW_TEST'#" $TESTPATH/lib/python/ufw/util.py
sed -i "s#proc = '/proc/net/if_inet6'#proc = '$TESTPATH/../good/reports/proc_net_if_inet6'#" $TESTPATH/lib/python/ufw/util.py
sed -i "s#proc = '/proc/net/dev'#proc = '$TESTPATH/../good/reports/proc_net_dev'#" $TESTPATH/lib/python/ufw/util.py
sed -i "s#\(.*\)\(addr = .* 0x8915,.*\)#\\1if ifname == 'eth0':\n\\1\\1addr = '10.0.2.9'\n\\1elif ifname == 'eth1':\n\\1\\1addr = '10.0.2.101'\n\\1else:\n\\1\\1raise IOError\n    return normalize_address(addr, v6)[0]\n    \\2#" $TESTPATH/lib/python/ufw/util.py

do_cmd "0" show listening

echo "show listening with rules" >> $TESTTMP/result
sed -i "s/IPV6=.*/IPV6=yes/" $TESTPATH/etc/default/ufw

for i in "" "in on eth0" ; do
    if [ -z "$i" ]; then
        do_cmd "0" null allow in 123
        do_cmd "0" null allow in OpenNTPD
        do_cmd "0" null allow in 123/tcp
    else
        do_cmd "0" null allow out 123
        do_cmd "0" null allow out 123/udp
        do_cmd "0" null allow out 123/tcp
    fi

    do_cmd "0" null allow $i to any
    do_cmd "0" null allow $i to any proto udp
    do_cmd "0" null allow $i to any proto tcp

    do_cmd "0" null allow $i to 10.0.2.101
    do_cmd "0" null allow $i to 10.0.2.9
    do_cmd "0" null allow $i to 10.0.0.0/16
    do_cmd "0" null allow $i to 10.0.2.0/24
    do_cmd "0" null allow $i to 10.0.3.0/24
    do_cmd "0" null allow $i to fe80::211:aaaa:bbbb:d54c

    do_cmd "0" null allow $i to 10.0.2.101 port 123
    do_cmd "0" null allow $i to 10.0.0.0/16 port 123
    do_cmd "0" null allow $i to 10.0.2.0/24 port 123
    do_cmd "0" null allow $i to 10.0.3.0/24 port 123
    do_cmd "0" null allow $i to fe80::211:aaaa:bbbb:d54c port 123

    do_cmd "0" null allow $i to 10.0.2.101 port 123 proto udp
    do_cmd "0" null allow $i to 10.0.0.0/16 app OpenNTPD
    do_cmd "0" null allow $i to 10.0.2.0/24 port 123 proto udp
    do_cmd "0" null allow $i to 10.0.3.0/24 port 123 proto udp
    do_cmd "0" null allow $i to fe80::211:aaaa:bbbb:d54c port 123 proto udp

    do_cmd "0" null allow $i to 10.0.2.101 port 123 proto tcp
    do_cmd "0" null allow $i to 10.0.0.0/16 port 123 proto tcp
    do_cmd "0" null allow $i to 10.0.2.0/24 port 123 proto tcp
    do_cmd "0" null allow $i to 10.0.3.0/24 port 123 proto tcp
    do_cmd "0" null allow $i to fe80::211:aaaa:bbbb:d54c port 123 proto tcp
done

do_cmd "0" show listening

exit 0
