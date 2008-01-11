#!/bin/bash

#set -x

# disable checks for test run
#sed -i 's/disableChecks = False/disableChecks = True/' $TESTPATH/usr/sbin/ufw

# example usage for successful run
#$TESTPATH/usr/sbin/ufw help >> $TESTTMP/result 2>&1 || exit 1

# example usage for failed run
#$TESTPATH/usr/sbin/ufw logging >> $TESTTMP/result 2>&1 && exit 1

# remove this when implementing real test
touch $TESTTMP/result || exit 1

exit 0

