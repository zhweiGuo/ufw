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
do_cmd "0" --dry-run deny proto tcp from 2001:db8::/32 to any port 25

echo "TO/FROM" >> $TESTTMP/result
from="2001:db8::/32"
to="2001:db8:3:4:5:6:7:8"
for x in allow deny
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

	do_cmd "0" --dry-run $x to $to port smtp from $from port ssh
	do_cmd "0" --dry-run delete $x to $to port smtp from $from port ssh
	do_cmd "0" --dry-run $x to $to port tftp from $from port ssh
	do_cmd "0" --dry-run delete $x to $to port tftp from $from port ssh
	do_cmd "0" --dry-run $x to $to port ssh from $from port domain
	do_cmd "0" --dry-run delete $x to $to port ssh from $from port domain
done

echo "Netmasks" >> $TESTTMP/result
do_cmd "0" --dry-run allow to ::1/0
do_cmd "0" --dry-run allow to ::1/32
do_cmd "0" --dry-run allow to ::1/128
do_cmd "0" --dry-run allow from ::1/0
do_cmd "0" --dry-run allow from ::1/32
do_cmd "0" --dry-run allow from ::1/128
do_cmd "0" --dry-run allow from ::1/32 to ::1/128

exit 0
