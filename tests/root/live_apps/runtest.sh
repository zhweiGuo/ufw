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

sed -i 's/debugging = False/debugging = True/' $TESTPATH/lib/python/ufw/util.py

echo "TESTING APPLICATION RULES" >> $TESTTMP/result
for ipv6 in yes no
do
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

	sed -i 's/137/9999/g' $TESTPATH/etc/ufw/applications.d/samba
	sed -i 's/80/8888/g' $TESTPATH/etc/ufw/applications.d/apache
	do_cmd "0"  app update Apache
	do_cmd "0"  app update Samba
	do_cmd "0" status
	do_cmd "0" status verbose

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
	do_cmd "0" status verbose
done

echo "TESTING APPLICATION RULES (v6 app rules)" >> $TESTTMP/result
do_cmd "0"  disable 
do_cmd "0"  enable
do_cmd "0"  allow Apache
do_cmd "0"  allow from 2001:db8::/32 to any app Apache
do_cmd "0"  delete allow from 2001:db8::/32 to any app Apache
do_cmd "0" status verbose


do_cmd "0"  disable 

exit 0
