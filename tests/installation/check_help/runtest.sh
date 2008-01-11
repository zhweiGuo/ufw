#!/bin/bash

sed -i 's/disableChecks = False/disableChecks = True/' $TESTPATH/usr/sbin/ufw
$TESTPATH/usr/sbin/ufw help >> $TESTTMP/result || exit 1

exit 0
