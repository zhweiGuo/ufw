#!/bin/bash

$TESTPATH/usr/sbin/ufw status >> $TESTTMP/result 2>&1 && exit 1

exit 0
