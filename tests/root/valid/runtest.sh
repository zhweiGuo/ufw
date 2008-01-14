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
do_cmd  logging off 
do_cmd  LOGGING ON 
do_cmd  LOGGING OFF 

echo "TESTING ARGS (enable/disable)" >> $TESTTMP/result
do_cmd  enable 
do_cmd  disable 
do_cmd  ENABLE 
do_cmd  DISABLE 

echo "TESTING ARGS (allow/deny port)" >> $TESTTMP/result
do_cmd  allow 25 
do_cmd  deny 25 
do_cmd  deny 1 
do_cmd  deny 65535 

echo "TESTING ARGS (allow/deny to/from)" >> $TESTTMP/result
do_cmd  allow 25 from 192.168.0.1 to 192.168.0.2 
do_cmd  deny 25 from 192.168.0.1 to 192.168.0.2 
do_cmd  allow 25 from 192.168.0.1 
do_cmd  deny 25 from 192.168.0.1 
do_cmd  allow 25 to 192.168.0.2 
do_cmd  deny 25 to 192.168.0.2 

do_cmd  allow 25 to 192.168.0.0/24 
do_cmd  deny 25 to 192.168.0.0/24 
do_cmd  allow 25 to 192.168.0.0/32 
do_cmd  deny 25 to 192.168.0.0/32 
do_cmd  allow 25 to 192.168.0.0/12 
do_cmd  deny 25 to 192.168.0.0/12 
do_cmd  allow 25 to 0.0.0.0/0 
do_cmd  deny 25 to 0.0.0.0/0 

echo "TESTING ARGS (status)" >> $TESTTMP/result
do_cmd  status 

exit 0
