#!/bin/bash

sed -i 's/disableChecks = False/disableChecks = True/' $TESTPATH/usr/sbin/ufw

let count=0
do_cmd() {
	echo "$count: $@" >> $TESTTMP/result
        $@ >> $TESTTMP/result 2>&1 || exit 1
	let count=count+1
	echo "" >> $TESTTMP/result
	echo "" >> $TESTTMP/result
}

echo "SIMPLE" >> $TESTTMP/result
do_cmd /tmp/ufw/usr/sbin/ufw --dry-run allow 25
do_cmd /tmp/ufw/usr/sbin/ufw --dry-run allow 25:tcp
do_cmd /tmp/ufw/usr/sbin/ufw --dry-run allow 25:udp
do_cmd /tmp/ufw/usr/sbin/ufw --dry-run allow 10.0.0.1

echo "TO/FROM" >> $TESTTMP/result
from="192.168.0.1"
to="10.0.0.1"
for x in allow deny
do
	do_cmd /tmp/ufw/usr/sbin/ufw --dry-run $x from $from
	do_cmd /tmp/ufw/usr/sbin/ufw --dry-run $x to $to
	do_cmd /tmp/ufw/usr/sbin/ufw --dry-run $x to $to from $from

	do_cmd /tmp/ufw/usr/sbin/ufw --dry-run $x from $from 80
	do_cmd /tmp/ufw/usr/sbin/ufw --dry-run $x to $to 25
	do_cmd /tmp/ufw/usr/sbin/ufw --dry-run $x to $to from $from 80
	do_cmd /tmp/ufw/usr/sbin/ufw --dry-run $x to $to 25 from $from
	do_cmd /tmp/ufw/usr/sbin/ufw --dry-run $x to $to 25 from $from 80
	for y in udp tcp
	do
		do_cmd /tmp/ufw/usr/sbin/ufw --dry-run $x from $from 80:$y
		do_cmd /tmp/ufw/usr/sbin/ufw --dry-run $x to $to 25:$y
		do_cmd /tmp/ufw/usr/sbin/ufw --dry-run $x to $to from $from 80:$y 
		do_cmd /tmp/ufw/usr/sbin/ufw --dry-run $x to $to 25:$y from $from
		do_cmd /tmp/ufw/usr/sbin/ufw --dry-run $x to $to 25:$y from $from 80:$y
	done
done

exit 0
