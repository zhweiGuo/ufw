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

echo "TESTING ARGS (logging)" >> $TESTTMP/result
do_cmd $TESTPATH/usr/sbin/ufw --dry-run logging on 
do_cmd $TESTPATH/usr/sbin/ufw --dry-run logging off 
do_cmd $TESTPATH/usr/sbin/ufw --dry-run LOGGING ON 
do_cmd $TESTPATH/usr/sbin/ufw --dry-run LOGGING OFF 

echo "TESTING ARGS (enable/disable)" >> $TESTTMP/result || exit 1
do_cmd $TESTPATH/usr/sbin/ufw --dry-run enable 
do_cmd $TESTPATH/usr/sbin/ufw --dry-run disable 
do_cmd $TESTPATH/usr/sbin/ufw --dry-run ENABLE 
do_cmd $TESTPATH/usr/sbin/ufw --dry-run DISABLE 

echo "TESTING ARGS (status)" >> $TESTTMP/result || exit 1
do_cmd $TESTPATH/usr/sbin/ufw --dry-run status

exit 0
