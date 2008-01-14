#!/bin/bash

sed -i 's/disableChecks = False/disableChecks = True/' $TESTPATH/usr/sbin/ufw

let count=0
do_cmd() {
        echo "$count: $@" >> $TESTTMP/result
        $TESTPATH/usr/sbin/ufw $@ >> $TESTTMP/result 2>&1 || exit 1
        let count=count+1
        echo "" >> $TESTTMP/result
        echo "" >> $TESTTMP/result
}

echo "TESTING ARGS (logging)" >> $TESTTMP/result
do_cmd  logging on 
grep "LOG" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result
do_cmd  logging off 
grep "LOG" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result
do_cmd  LOGGING ON 
grep "LOG" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result
do_cmd  LOGGING OFF 
grep "LOG" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result

echo "TESTING ARGS (default)" >> $TESTTMP/result
do_cmd  default allow
head $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result
do_cmd  default deny
head $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result
do_cmd  DEFAULT ALLOW
head $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result
do_cmd  DEFAULT DENY
head $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result

echo "TESTING ARGS (enable/disable)" >> $TESTTMP/result
do_cmd  enable 
cat $TESTPATH/etc/default/ufw >> $TESTTMP/result
do_cmd  disable 
cat $TESTPATH/etc/default/ufw >> $TESTTMP/result
do_cmd  ENABLE 
cat $TESTPATH/etc/default/ufw >> $TESTTMP/result
do_cmd  DISABLE 
cat $TESTPATH/etc/default/ufw >> $TESTTMP/result

echo "TESTING ARGS (allow/deny port)" >> $TESTTMP/result
do_cmd  allow 25 
do_cmd  deny 25 
do_cmd  deny 1 
do_cmd  deny 65535 
grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result
do_cmd  delete allow 25 
do_cmd  delete deny 25 
do_cmd  delete deny 1 
do_cmd  delete deny 65535 
grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result


echo "TESTING ARGS (allow/deny to/from)" >> $TESTTMP/result
echo "Man page" >> $TESTTMP/result
do_cmd  allow 53
grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result
do_cmd  allow 25:tcp
grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result
do_cmd  deny to 80:tcp
grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result
do_cmd  deny from 10.0.0.0/8 to 192.168.0.1 25:tcp
grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result
do_cmd  deny 53
grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result
do_cmd  allow 80:tcp
grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result
do_cmd  allow from 10.0.0.0/8
grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result
do_cmd  allow from 172.16.0.0/12
grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result
do_cmd  allow from 192.168.0.0/16
grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result
do_cmd  deny from 1.2.3.4 to 514:udp
grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result
do_cmd  allow from 1.2.3.5 5469:udp to 1.2.3.4 5469:udp
grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result

do_cmd  delete allow 53
do_cmd  delete allow 25:tcp
do_cmd  delete deny to 80:tcp
do_cmd  delete deny from 10.0.0.0/8 to 192.168.0.1 25:tcp
do_cmd  delete deny 53
do_cmd  delete allow 80:tcp
do_cmd  delete allow from 10.0.0.0/8
do_cmd  delete allow from 172.16.0.0/12
do_cmd  delete allow from 192.168.0.0/16
do_cmd  delete deny from 1.2.3.4 to 514:udp
do_cmd  delete allow from 1.2.3.5 5469:udp to 1.2.3.4 5469:udp
grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result


echo "SIMPLE" >> $TESTTMP/result
do_cmd  allow 25
grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result
do_cmd  delete allow 25
grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result

do_cmd  allow 25:tcp
grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result
do_cmd  delete allow 25:tcp
grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result

do_cmd  allow 25:udp
grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result
do_cmd  delete allow 25:udp
grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result

do_cmd  allow 25
grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result
do_cmd  delete allow 25
grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result

do_cmd  allow 25:tcp
grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result
do_cmd  delete allow 25:tcp
grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result

do_cmd  allow 25:udp
grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result
do_cmd  delete allow 25:udp
grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result

echo "TO/FROM" >> $TESTTMP/result
from="192.168.0.1"
to="10.0.0.1"
for x in allow deny
do
        do_cmd  $x from $from
	grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result
        do_cmd  delete $x from $from
	grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result
        do_cmd  $x to $to
	grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result
        do_cmd  delete $x to $to
	grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result
        do_cmd  $x to $to from $from
	grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result
        do_cmd  delete $x to $to from $from
	grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result

        do_cmd  $x from $from 80
	grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result
        do_cmd  delete $x from $from 80
	grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result
        do_cmd  $x to $to 25
	grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result
        do_cmd  delete $x to $to 25
	grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result
        do_cmd  $x to $to from $from 80
	grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result
        do_cmd  delete $x to $to from $from 80
	grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result
        do_cmd  $x to $to 25 from $from
	grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result
        do_cmd  delete $x to $to 25 from $from
	grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result
        do_cmd  $x to $to 25 from $from 80
	grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result
        do_cmd  delete $x to $to 25 from $from 80
	grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result
        for y in udp tcp
        do
                do_cmd  $x from $from 80:$y
		grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result
                do_cmd  delete $x from $from 80:$y
		grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result
                do_cmd  $x to $to 25:$y
		grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result
                do_cmd  delete $x to $to 25:$y
		grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result
                do_cmd  $x to $to from $from 80:$y
		grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result
                do_cmd  delete $x to $to from $from 80:$y
		grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result
                do_cmd  $x to $to 25:$y from $from
		grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result
                do_cmd  delete $x to $to 25:$y from $from
		grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result
                do_cmd  $x to $to 25:$y from $from 80:$y
		grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result
                do_cmd  delete $x to $to 25:$y from $from 80:$y
		grep -A2 "tuple" $TESTPATH/etc/ufw/ufw.rules >> $TESTTMP/result
        done
done

echo "TESTING ARGS (status)" >> $TESTTMP/result
do_cmd --dry-run status 

exit 0
