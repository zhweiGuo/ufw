#!/bin/bash

sed -i 's/disableChecks = False/disableChecks = True/' $TESTPATH/usr/sbin/ufw

let count=0
do_cmd() {
        echo "$count: $@" >> $TESTTMP/result
        res=`$TESTPATH/usr/sbin/ufw $@ 2>&1`
        if [ "$?" == 0 ]; then
		echo $res >> $TESTTMP/result
		exit 1
	fi
        let count=count+1
        echo "" >> $TESTTMP/result
        echo "" >> $TESTTMP/result
}

echo "TESTING ARGS (logging)" >> $TESTTMP/result
do_cmd --dry-run logging
do_cmd --dry-run logging foo
do_cmd --dry-run loggin on

echo "TESTING ARGS (default)" >> $TESTTMP/result
do_cmd --dry-run default
do_cmd --dry-run default foo
do_cmd --dry-run default accept
do_cmd --dry-run defaul allow

echo "TESTING ARGS (enable/disable)" >> $TESTTMP/result
# bad
do_cmd --dry-run enabled
do_cmd --dry-run disabled

echo "TESTING ARGS (allow/deny)" >> $TESTTMP/result
do_cmd --dry-run allow
do_cmd --dry-run deny

echo "TESTING ARGS (allow/deny bad port)" >> $TESTTMP/result
do_cmd --dry-run alow 25
do_cmd --dry-run dny 25
do_cmd --dry-run allow 25a
do_cmd --dry-run deny 25a
do_cmd --dry-run allow 65536
do_cmd --dry-run deny 65536
do_cmd --dry-run allow 0
do_cmd --dry-run deny 0

echo "TESTING ARGS (allow/deny bad to/from)" >> $TESTTMP/result
do_cmd --dry-run allow 25 to
do_cmd --dry-run deny 25 to
do_cmd --dry-run allow 25 from
do_cmd --dry-run deny 25 from
do_cmd --dry-run allow 25 from 192.168.0.1 to
do_cmd --dry-run deny 25 from 192.168.0.1 to
do_cmd --dry-run allow 25 from 192.168.0.1 from
do_cmd --dry-run deny 25 from 192.168.0.1 from
do_cmd --dry-run allow 25 to 192.168.0.1 from
do_cmd --dry-run deny 25 to 192.168.0.1 from
do_cmd --dry-run allow 25 to 192.168.0.1 to
do_cmd --dry-run deny 25 to 192.168.0.1 to
do_cmd --dry-run allow 25 to from 192.168.0.1
do_cmd --dry-run deny 25 to from 192.168.0.1
do_cmd --dry-run allow 25 from to 192.168.0.1
do_cmd --dry-run deny 25 from to 192.168.0.1
do_cmd --dry-run allow 25 from from 192.168.0.1
do_cmd --dry-run deny 25 from from 192.168.0.1
do_cmd --dry-run allow 25 to to 192.168.0.1
do_cmd --dry-run deny 25 to to 192.168.0.1

echo "TESTING ARGS (allow/deny bad ip)" >> $TESTTMP/result
do_cmd --dry-run allow 25 to 192.168.0.
do_cmd --dry-run allow 25 to 192.168.0.1.1
do_cmd --dry-run allow 25 to foo
do_cmd --dry-run allow 25 to xxx.xxx.xxx.xx
do_cmd --dry-run allow 25 to 192a.168.0.1
do_cmd --dry-run allow 25 to 192.168a.0.1
do_cmd --dry-run allow 25 to 192.168.0a.1
do_cmd --dry-run allow 25 to 192.168.1.a1
do_cmd --dry-run allow 25 to 192.168.1..1
do_cmd --dry-run allow 25 to 192.168.1..1/24
do_cmd --dry-run allow 25 to 192.168.1.256
do_cmd --dry-run allow 25 to 256.0.0.0
do_cmd --dry-run allow 25 to 10.256.0.0

echo "TESTING ARGS (delete allow/deny)" >> $TESTTMP/result
do_cmd --dry-run delete


exit 0
