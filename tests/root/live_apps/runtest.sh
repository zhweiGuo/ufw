#!/bin/bash

#    Copyright 2008-2009 Canonical Ltd.
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

echo "TESTING APPLICATION RULES" >> $TESTTMP/result
for update in no yes
do
    if [ "$update" = "yes" ]; then
        echo "Adding and deleting updated app rules" >> $TESTTMP/result
    else
        echo "Adding and deleting app rules" >> $TESTTMP/result
    fi
    for ipv6 in yes no
    do
        # make sure we always start clean
        sed -i 's/9999/137/g' $TESTPATH/etc/ufw/applications.d/samba
        sed -i 's/8888/80/g' $TESTPATH/etc/ufw/applications.d/apache

	echo "Setting IPV6 to $ipv6" >> $TESTTMP/result
	sed -i "s/IPV6=.*/IPV6=$ipv6/" $TESTPATH/etc/default/ufw
	do_cmd "0"  disable
	do_cmd "0"  enable

	do_cmd "0"  allow Apache
	for loc in any addr ; do
		if [ "$loc" != "any" ]; then
			if [ "$ipv6" = "yes" ]; then
				loc="2001:db8::/32"
			else
				loc="192.168.2.0/24"
			fi
		fi
		do_cmd "0"  allow to $loc app Samba
		do_cmd "0"  allow from $loc app Samba
		do_cmd "0"  allow to $loc app Samba from $loc app Bind9
		do_cmd "0"  allow to $loc app Samba from $loc port 22
		do_cmd "0"  allow to $loc app Apache from $loc port 88
	done
	do_cmd "0" status
	do_cmd "0" status verbose

        if [ "$update" = "yes" ]; then
	    sed -i 's/137/9999/g' $TESTPATH/etc/ufw/applications.d/samba
	    sed -i 's/80/8888/g' $TESTPATH/etc/ufw/applications.d/apache
	    do_cmd "0"  app update Apache
	    do_cmd "0"  app update Samba
	    do_cmd "0" status
	    do_cmd "0" status verbose
        fi

	do_cmd "0"  delete allow Apache
	for loc in any addr ; do
		if [ "$loc" != "any" ]; then
			if [ "$ipv6" = "yes" ]; then
				loc="2001:db8::/32"
			else
				loc="192.168.2.0/24"
			fi
		fi
		do_cmd "0"  delete allow to $loc app Samba
		do_cmd "0"  delete allow from $loc app Samba
		do_cmd "0"  delete allow to $loc app Samba from $loc app Bind9
		do_cmd "0"  delete allow to $loc app Samba from $loc port 22
		do_cmd "0"  delete allow to $loc app Apache from $loc port 88
	done
	do_cmd "0" status
    done
done

sed -i 's/9999/137/g' $TESTPATH/etc/ufw/applications.d/samba
sed -i 's/8888/80/g' $TESTPATH/etc/ufw/applications.d/apache

echo "TESTING APPLICATION RULES (v6 delete app rules)" >> $TESTTMP/result
echo "Setting IPV6 to yes" >> $TESTTMP/result
sed -i "s/IPV6=.*/IPV6=yes/" $TESTPATH/etc/default/ufw
do_cmd "0"  disable
do_cmd "0"  enable
do_cmd "0"  allow Apache
do_cmd "0"  allow from 2001:db8::/32 to any app Apache
do_cmd "0" status verbose
do_cmd "0"  delete allow from 2001:db8::/32 to any app Apache
do_cmd "0" status verbose
do_cmd "0" delete allow Apache
do_cmd "0" status verbose

echo "TESTING APPLICATION RULES (update)" >> $TESTTMP/result
# some of these are ommitted cause they are above
do_cmd "0" app update Bind9
do_cmd "0" app default allow
do_cmd "0" app update --add-new Apache
do_cmd "0" app default deny
do_cmd "0" app update --add-new Samba
do_cmd "0" app default skip
do_cmd "0" app update --add-new Bind9
do_cmd "0" status verbose
do_cmd "0"  delete allow Apache
do_cmd "0"  delete deny Samba
do_cmd "0" status verbose


echo "TESTING APPLICATION INTEGRATION (exact vs multi)" >> $TESTTMP/result
cat > $TESTPATH/etc/ufw/applications.d/Runtest2 << EOM
[Runtest2]
title=runtest title
description=runtest description
ports=23/tcp
EOM
cat > $TESTPATH/etc/ufw/applications.d/RunTest2 << EOM
[RunTest2]
title=runtest title
description=runtest description
ports=24/tcp
EOM
do_cmd "0" allow RunTest2
do_cmd "0" status verbose
do_cmd "0" delete allow RunTest2
do_cmd "0" status verbose

echo "TESTING APPLICATION INTEGRATION (case insensitive)" >> $TESTTMP/result
cat > $TESTPATH/etc/ufw/applications.d/runtest << EOM
[runtest]
title=runtest title
description=runtest description
ports=26/tcp
EOM
do_cmd "0" allow runtest
do_cmd "0" status verbose
do_cmd "0" deny RunTest
do_cmd "0" status verbose
do_cmd "0" delete deny RUNTESt

echo "TESTING APPLICATION INTEGRATION (reject)" >> $TESTTMP/result
do_cmd "0" reject to any from any app Samba
do_cmd "0" reject Samba
do_cmd "0" status verbose
do_cmd "0" delete reject to any from any app Samba
do_cmd "0" delete reject Samba
do_cmd "0" status verbose


echo "TESTING INSERT" >> $TESTTMP/result
for ipv6 in no yes ; do
    echo "Setting IPV6 to $ipv6" >> $TESTTMP/result
    sed -i "s/IPV6=.*/IPV6=$ipv6/" $TESTPATH/etc/default/ufw
    do_cmd "0"  disable
    do_cmd "0"  enable
    do_cmd "0" allow Apache
    do_cmd "0" allow Bind9
    do_cmd "0" insert 1 allow Samba
    do_cmd "0" insert 2 reject 'Dovecot POP3'
    cat $TESTPATH/var/lib/ufw/user.rules >> $TESTTMP/result
    cat $TESTPATH/var/lib/ufw/user6.rules >> $TESTTMP/result

    iptables-save | egrep -v '^(#|:)' > $TESTTMP/save.1
    ip6tables-save | egrep -v '^(#|:)' >> $TESTTMP/save.1
    do_cmd "0"  disable
    do_cmd "0"  enable
    iptables-save | egrep -v '^(#|:)' > $TESTTMP/save.2
    ip6tables-save | egrep -v '^(#|:)' >> $TESTTMP/save.2
    diff $TESTTMP/save.1 $TESTTMP/save.2 || {
        echo "ip(6)tables-restore different for '$i'"
        exit 1
    }

    do_cmd "0" delete allow Apache
    do_cmd "0" delete allow Bind9
    do_cmd "0" delete allow Samba
    do_cmd "0" delete reject 'Dovecot POP3'
    cat $TESTPATH/var/lib/ufw/user.rules >> $TESTTMP/result
    cat $TESTPATH/var/lib/ufw/user6.rules >> $TESTTMP/result

    do_cmd "0" allow Samba
    do_cmd "0" allow 22
    do_cmd "0" insert 2 allow from any to any app Samba
    do_cmd "0" insert 2 allow from 192.168.0.1 to 10.0.0.1 app Samba
    do_cmd "0" insert 2 allow from 192.168.0.1 to any app Samba
    do_cmd "0" insert 2 allow from 192.168.0.1 app Samba to 10.0.0.1
    do_cmd "0" insert 2 allow from any app Samba to 10.0.0.1
    cat $TESTPATH/var/lib/ufw/user.rules >> $TESTTMP/result
    cat $TESTPATH/var/lib/ufw/user6.rules >> $TESTTMP/result

    iptables-save | egrep -v '^(#|:)' > $TESTTMP/save.1
    ip6tables-save | egrep -v '^(#|:)' >> $TESTTMP/save.1
    do_cmd "0"  disable
    do_cmd "0"  enable
    iptables-save | egrep -v '^(#|:)' > $TESTTMP/save.2
    ip6tables-save | egrep -v '^(#|:)' >> $TESTTMP/save.2
    diff $TESTTMP/save.1 $TESTTMP/save.2 || {
        echo "ip(6)tables-restore different for '$i'"
        exit 1
    }

    do_cmd "0" delete allow Samba
    do_cmd "0" delete allow 22
    do_cmd "0" delete allow from any to any app Samba
    do_cmd "0" delete allow from 192.168.0.1 to 10.0.0.1 app Samba
    do_cmd "0" delete allow from 192.168.0.1 to any app Samba
    do_cmd "0" delete allow from 192.168.0.1 app Samba to 10.0.0.1
    do_cmd "0" delete allow from any app Samba to 10.0.0.1
    cat $TESTPATH/var/lib/ufw/user.rules >> $TESTTMP/result
    cat $TESTPATH/var/lib/ufw/user6.rules >> $TESTTMP/result
done

cleanup

exit 0
