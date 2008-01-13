#!/bin/bash

sed -i 's/disableChecks = False/disableChecks = True/' $TESTPATH/usr/sbin/ufw
$TESTPATH/usr/sbin/ufw --dry-run status >> $TESTTMP/result 2>&1 || exit 1

exit 0
