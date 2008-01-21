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

sed -i 's/disable_checks = False/disable_checks = True/' $TESTPATH/usr/sbin/ufw

let count=0
do_cmd() {
	echo "$count: $@" >> $TESTTMP/result
        $TESTPATH/usr/sbin/ufw $@ >> $TESTTMP/result 2>&1 || exit 1
	let count=count+1
	echo "" >> $TESTTMP/result
	echo "" >> $TESTTMP/result
}

echo "Man page" >> $TESTTMP/result
do_cmd --dry-run allow 53
do_cmd --dry-run allow 25:tcp
do_cmd --dry-run deny to 80:tcp
do_cmd --dry-run deny from 10.0.0.0/8 to 192.168.0.1 25:tcp
do_cmd --dry-run deny 53
do_cmd --dry-run deny smtp
do_cmd --dry-run allow 80:tcp
do_cmd --dry-run allow from 10.0.0.0/8
do_cmd --dry-run allow from 172.16.0.0/12
do_cmd --dry-run allow from 192.168.0.0/16
do_cmd --dry-run deny from 1.2.3.4 to 514:udp
do_cmd --dry-run allow from 1.2.3.5 5469:udp to 1.2.3.4 5469:udp

echo "SIMPLE" >> $TESTTMP/result
do_cmd --dry-run allow 25
do_cmd --dry-run allow 25:tcp
do_cmd --dry-run allow 25:udp
do_cmd --dry-run delete allow 25
do_cmd --dry-run delete allow 25:tcp
do_cmd --dry-run delete allow 25:udp

echo "TO/FROM" >> $TESTTMP/result
from="192.168.0.1"
to="10.0.0.1"
for x in allow deny
do
	do_cmd --dry-run $x from $from
	do_cmd --dry-run delete $x from $from
	do_cmd --dry-run $x to $to
	do_cmd --dry-run delete $x to $to
	do_cmd --dry-run $x to $to from $from
	do_cmd --dry-run delete $x to $to from $from

	do_cmd --dry-run $x from $from 80
	do_cmd --dry-run delete $x from $from 80
	do_cmd --dry-run $x to $to 25
	do_cmd --dry-run delete $x to $to 25
	do_cmd --dry-run $x to $to from $from 80
	do_cmd --dry-run delete $x to $to from $from 80
	do_cmd --dry-run $x to $to 25 from $from
	do_cmd --dry-run delete $x to $to 25 from $from
	do_cmd --dry-run $x to $to 25 from $from 80
	do_cmd --dry-run delete $x to $to 25 from $from 80
	for y in udp tcp
	do
		do_cmd --dry-run $x from $from 80:$y
		do_cmd --dry-run delete $x from $from 80:$y
		do_cmd --dry-run $x to $to 25:$y
		do_cmd --dry-run delete $x to $to 25:$y
		do_cmd --dry-run $x to $to from $from 80:$y 
		do_cmd --dry-run delete $x to $to from $from 80:$y 
		do_cmd --dry-run $x to $to 25:$y from $from
		do_cmd --dry-run delete $x to $to 25:$y from $from
		do_cmd --dry-run $x to $to 25:$y from $from 80:$y
		do_cmd --dry-run delete $x to $to 25:$y from $from 80:$y
	done
done

exit 0
