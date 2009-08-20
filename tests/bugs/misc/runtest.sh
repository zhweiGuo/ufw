#!/bin/bash

#    Copyright 2009 Canonical Ltd.
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

echo "Bug #319226" >> $TESTTMP/result
mkdir $TESTPATH/etc/ufw/applications.d/.svn
touch $TESTPATH/etc/ufw/applications.d/.hgignore
cat > $TESTPATH/etc/ufw/applications.d/.testme << EOM
[Bug319226]
title=test 319226
description=test description
ports=23/tcp
EOM
do_cmd "0" app list

echo "Bug #337705" >> $TESTTMP/result
sed -i 's/import ufw.frontend/import ufw.nonexistent/' $TESTPATH/usr/sbin/ufw
do_cmd "1" help
sed -i 's/import ufw.nonexistent/import ufw.frontend/' $TESTPATH/usr/sbin/ufw

echo "Bug (Samba IPV4 tuple text wrong when IPV6 is enabled" >> $TESTTMP/result
sed -i 's/IPV6=.*/IPV6=yes/' $TESTPATH/etc/default/ufw
do_cmd "0" allow in on eth1 to any app Samba
grep -A2 "tuple" $TESTSTATE/user.rules >> $TESTTMP/result
grep -A2 "tuple" $TESTSTATE/user6.rules >> $TESTTMP/result
do_cmd "0" null delete allow in on eth1 to any app Samba
sed -i 's/IPV6=.*/IPV6=no/' $TESTPATH/etc/default/ufw

echo "Bug (inserted Samba rules out of order when IPV6 is enabled" >> $TESTTMP/result
sed -i 's/IPV6=.*/IPV6=yes/' $TESTPATH/etc/default/ufw
do_cmd "0" allow in on eth0
do_cmd "0" allow to 192.168.0.2
do_cmd "0" allow to 192.168.0.3
do_cmd "0" allow in on eth1
do_cmd "0" allow in on eth2
do_cmd "0" insert 8 deny to any app Bind9
grep "^-A .*user-input" $TESTSTATE/user.rules >> $TESTTMP/result
grep "^-A .*user-input" $TESTSTATE/user6.rules >> $TESTTMP/result

do_cmd "0" delete deny to any app Bind9
do_cmd "0" insert 8 deny to any app Samba
grep "^-A .*user-input" $TESTSTATE/user.rules >> $TESTTMP/result
grep "^-A .*user-input" $TESTSTATE/user6.rules >> $TESTTMP/result

# this insert should look the same as the above
do_cmd "0" delete deny to any app Samba
do_cmd "0" insert 5 deny to any app Bind9
grep "^-A .*user-input" $TESTSTATE/user.rules >> $TESTTMP/result
grep "^-A .*user-input" $TESTSTATE/user6.rules >> $TESTTMP/result

do_cmd "0" delete deny to any app Bind9
do_cmd "0" insert 5 deny to any app Samba
grep "^-A .*user-input" $TESTSTATE/user.rules >> $TESTTMP/result
grep "^-A .*user-input" $TESTSTATE/user6.rules >> $TESTTMP/result

do_cmd "0" delete allow in on eth0
do_cmd "0" delete allow to 192.168.0.2
do_cmd "0" delete allow to 192.168.0.3
do_cmd "0" delete allow in on eth1
do_cmd "0" delete allow in on eth2
do_cmd "0" delete deny to any app Samba
grep "^-A .*user-input" $TESTSTATE/user.rules >> $TESTTMP/result
grep "^-A .*user-input" $TESTSTATE/user6.rules >> $TESTTMP/result
sed -i 's/IPV6=.*/IPV6=no/' $TESTPATH/etc/default/ufw

exit 0
