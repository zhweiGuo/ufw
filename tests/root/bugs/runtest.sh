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

# setup
do_cmd "0"  disable
do_cmd "0"  enable

echo "Bug #247352" >> $TESTTMP/result
do_cmd "0" --dry-run allow http/tcp
grep -A2 "tuple" $TESTPATH/var/lib/ufw/user.rules >> $TESTTMP/result
echo "iptables -L -n:" >> $TESTTMP/result
iptables -L -n | grep -A2 "80" >> $TESTTMP/result 2>&1
do_cmd "0" delete allow http/tcp
grep -A2 "tuple" $TESTPATH/var/lib/ufw/user.rules >> $TESTTMP/result

echo "Bug #251355" >> $TESTTMP/result
echo "Setting IPV6 to no" >> $TESTTMP/result
sed -i "s/IPV6=.*/IPV6=no/" $TESTPATH/etc/default/ufw
do_cmd "0"  disable
do_cmd "0"  enable
echo "/etc/init.d/ufw force-reload:" >> $TESTTMP/result
$TESTPATH/etc/init.d/ufw force-reload >> $TESTTMP/result 2>&1
echo "ip6tables -L -n:" >> $TESTTMP/result
ip6tables -L -n >> $TESTTMP/result 2>&1

echo "Bug #260881" >> $TESTTMP/result
echo "Setting IPV6 to no" >> $TESTTMP/result
sed -i "s/IPV6=.*/IPV6=no/" $TESTPATH/etc/default/ufw
do_cmd "0"  disable
do_cmd "0"  enable
do_cmd "0"  allow Apache
do_cmd "0"  delete deny Apache
echo "iptables -L -n:" >> $TESTTMP/result
iptables -L -n | grep -A2 "80" >> $TESTTMP/result 2>&1
do_cmd "0"  delete allow Apache
echo "iptables -L -n:" >> $TESTTMP/result
iptables -L -n | grep -A2 "80" >> $TESTTMP/result 2>&1

echo "Bug #263308" >> $TESTTMP/result
echo "Setting IPV6 to yes" >> $TESTTMP/result
sed -i "s/IPV6=.*/IPV6=yes/" $TESTPATH/etc/default/ufw
do_cmd "0"  disable
do_cmd "0"  enable
do_cmd "0"  allow to any from any
do_cmd "0"  allow proto tcp to any from any
do_cmd "0"  allow to 192.168.1.1
do_cmd "0"  allow proto udp from 192.168.1.1 to any
do_cmd "0"  allow from 192.168.1.1 to 192.168.1.2
do_cmd "0"  allow proto udp from 192.168.1.1 to 192.168.1.2
do_cmd "0"  status
do_cmd "0"  delete allow to any from any
do_cmd "0"  delete allow proto tcp to any from any
do_cmd "0"  delete allow to 192.168.1.1
do_cmd "0"  delete allow proto udp from 192.168.1.1 to any
do_cmd "0"  delete allow from 192.168.1.1 to 192.168.1.2
do_cmd "0"  delete allow proto udp from 192.168.1.1 to 192.168.1.2
do_cmd "0"  status

echo "Bug #273278" >> $TESTTMP/result
echo "Setting IPV6 to yes" >> $TESTTMP/result
sed -i "s/IPV6=.*/IPV6=yes/" $TESTPATH/etc/default/ufw
do_cmd "0"  disable
do_cmd "0"  enable
do_cmd "0"  status verbose
cat $TESTPATH/etc/ufw/after*.rules | egrep 'LOG .*UFW ' >> $TESTTMP/result
do_cmd "0"  default allow
do_cmd "0"  status verbose
cat $TESTPATH/etc/ufw/after*.rules | egrep 'LOG .*UFW ' >> $TESTTMP/result
do_cmd "0"  default deny
do_cmd "0"  status verbose
cat $TESTPATH/etc/ufw/after*.rules | egrep 'LOG .*UFW ' >> $TESTTMP/result

# teardown
do_cmd "0"  disable

exit 0
