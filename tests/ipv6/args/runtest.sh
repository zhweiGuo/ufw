#!/bin/bash

sed -i 's/IPV6=no/IPV6=yes/' $TESTPATH/etc/default/ufw
sed -i 's/disableChecks = False/disableChecks = True/' $TESTPATH/usr/sbin/ufw

echo "TESTING ARGS (enable/disable)" >> $TESTTMP/result || exit 1
$TESTPATH/usr/sbin/ufw --dry-run enable >> $TESTTMP/result 2>&1 || exit 1
$TESTPATH/usr/sbin/ufw --dry-run disable >> $TESTTMP/result 2>&1 || exit 1

echo "TESTING ARGS (status)" >> $TESTTMP/result || exit 1
$TESTPATH/usr/sbin/ufw --dry-run status >> $TESTTMP/result 2>&1 || exit 1

exit 0
