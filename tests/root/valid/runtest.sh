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
do_cmd "0"  logging on 
grep "LOG" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result
do_cmd "0"  logging off 
grep "LOG" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result
do_cmd "0"  LOGGING ON 
grep "LOG" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result
do_cmd "0"  LOGGING OFF 
grep "LOG" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result

echo "TESTING ARGS (default)" >> $TESTTMP/result
do_cmd "0"  default allow
head $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result
do_cmd "0"  default deny
head $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result
do_cmd "0"  DEFAULT ALLOW
head $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result
do_cmd "0"  DEFAULT DENY
head $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result

echo "TESTING ARGS (enable/disable)" >> $TESTTMP/result
do_cmd "0"  enable 
cat $TESTPATH/etc/default/ufw >> $TESTTMP/result
do_cmd "0"  disable 
cat $TESTPATH/etc/default/ufw >> $TESTTMP/result
do_cmd "0"  ENABLE 
cat $TESTPATH/etc/default/ufw >> $TESTTMP/result
do_cmd "0"  DISABLE 
cat $TESTPATH/etc/default/ufw >> $TESTTMP/result

echo "TESTING ARGS (allow/deny port)" >> $TESTTMP/result
do_cmd "0"  allow 25 
do_cmd "0"  deny 25 
do_cmd "0"  deny 1 
do_cmd "0"  deny 65535 
grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result
do_cmd "0"  delete allow 25 
do_cmd "0"  delete deny 25 
do_cmd "0"  delete deny 1 
do_cmd "0"  delete deny 65535 
grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result


echo "TESTING ARGS (allow/deny to/from)" >> $TESTTMP/result
echo "Man page" >> $TESTTMP/result
do_cmd "0"  allow 53
grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result
do_cmd "0"  allow 25:tcp
grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result
do_cmd "0"  deny to 80:tcp
grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result
do_cmd "0"  deny from 10.0.0.0/8 to 192.168.0.1 25:tcp
grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result
do_cmd "0"  deny 53
grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result
do_cmd "0"  allow 80:tcp
grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result
do_cmd "0"  allow from 10.0.0.0/8
grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result
do_cmd "0"  allow from 172.16.0.0/12
grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result
do_cmd "0"  allow from 192.168.0.0/16
grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result
do_cmd "0"  deny from 1.2.3.4 to 514:udp
grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result
do_cmd "0"  allow from 1.2.3.5 5469:udp to 1.2.3.4 5469:udp
grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result

do_cmd "0"  delete allow 53
do_cmd "0"  delete allow 25:tcp
do_cmd "0"  delete deny to 80:tcp
do_cmd "0"  delete deny from 10.0.0.0/8 to 192.168.0.1 25:tcp
do_cmd "0"  delete deny 53
do_cmd "0"  delete allow 80:tcp
do_cmd "0"  delete allow from 10.0.0.0/8
do_cmd "0"  delete allow from 172.16.0.0/12
do_cmd "0"  delete allow from 192.168.0.0/16
do_cmd "0"  delete deny from 1.2.3.4 to 514:udp
do_cmd "0"  delete allow from 1.2.3.5 5469:udp to 1.2.3.4 5469:udp
grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result


echo "SIMPLE" >> $TESTTMP/result
do_cmd "0"  allow 25
grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result
do_cmd "0"  delete allow 25
grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result

do_cmd "0"  allow 25:tcp
grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result
do_cmd "0"  delete allow 25:tcp
grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result

do_cmd "0"  allow 25:udp
grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result
do_cmd "0"  delete allow 25:udp
grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result

do_cmd "0"  allow 25
grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result
do_cmd "0"  delete allow 25
grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result

do_cmd "0"  allow 25:tcp
grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result
do_cmd "0"  delete allow 25:tcp
grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result

do_cmd "0"  allow 25:udp
grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result
do_cmd "0"  delete allow 25:udp
grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result

echo "TO/FROM" >> $TESTTMP/result
from="192.168.0.1"
to="10.0.0.1"
for x in allow deny
do
        do_cmd "0"  $x from $from
	grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result
        do_cmd "0"  delete $x from $from
	grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result
        do_cmd "0"  $x to $to
	grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result
        do_cmd "0"  delete $x to $to
	grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result
        do_cmd "0"  $x to $to from $from
	grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result
        do_cmd "0"  delete $x to $to from $from
	grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result

        do_cmd "0"  $x from $from 80
	grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result
        do_cmd "0"  delete $x from $from 80
	grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result
        do_cmd "0"  $x to $to 25
	grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result
        do_cmd "0"  delete $x to $to 25
	grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result
        do_cmd "0"  $x to $to from $from 80
	grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result
        do_cmd "0"  delete $x to $to from $from 80
	grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result
        do_cmd "0"  $x to $to 25 from $from
	grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result
        do_cmd "0"  delete $x to $to 25 from $from
	grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result
        do_cmd "0"  $x to $to 25 from $from 80
	grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result
        do_cmd "0"  delete $x to $to 25 from $from 80
	grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result
        for y in udp tcp
        do
                do_cmd "0"  $x from $from 80:$y
		grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result
                do_cmd "0"  delete $x from $from 80:$y
		grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result
                do_cmd "0"  $x to $to 25:$y
		grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result
                do_cmd "0"  delete $x to $to 25:$y
		grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result
                do_cmd "0"  $x to $to from $from 80:$y
		grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result
                do_cmd "0"  delete $x to $to from $from 80:$y
		grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result
                do_cmd "0"  $x to $to 25:$y from $from
		grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result
                do_cmd "0"  delete $x to $to 25:$y from $from
		grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result
                do_cmd "0"  $x to $to 25:$y from $from 80:$y
		grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result
                do_cmd "0"  delete $x to $to 25:$y from $from 80:$y
		grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result
        done
done

echo "TESTING ARGS (status)" >> $TESTTMP/result
do_cmd "0" --dry-run status 

exit 0
