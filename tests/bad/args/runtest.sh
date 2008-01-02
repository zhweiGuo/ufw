#!/bin/bash

echo "TESTING ARGS (logging)" >> $TESTTMP/result || exit 1
# bad
$TESTPATH/usr/sbin/ufw logging >> $TESTTMP/result 2>&1 && exit 1
$TESTPATH/usr/sbin/ufw logging foo >> $TESTTMP/result 2>&1 && exit 1
$TESTPATH/usr/sbin/ufw loggin on >> $TESTTMP/result 2>&1 && exit 1
# good
$TESTPATH/usr/sbin/ufw logging on >> $TESTTMP/result 2>&1 || exit 1
$TESTPATH/usr/sbin/ufw logging off >> $TESTTMP/result 2>&1 || exit 1

exit 0
