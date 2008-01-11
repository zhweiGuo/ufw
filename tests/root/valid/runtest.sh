#!/bin/bash

sed -i 's/disableChecks = False/disableChecks = True/' $TESTPATH/usr/sbin/ufw

echo "TESTING ARGS (logging)" >> $TESTTMP/result || exit 1
echo "1" >> $TESTTMP/result
$TESTPATH/usr/sbin/ufw  logging on >> $TESTTMP/result 2>&1 || exit 1
echo "2" >> $TESTTMP/result
$TESTPATH/usr/sbin/ufw  logging off >> $TESTTMP/result 2>&1 || exit 1
echo "3" >> $TESTTMP/result
$TESTPATH/usr/sbin/ufw  LOGGING ON >> $TESTTMP/result 2>&1 || exit 1
echo "4" >> $TESTTMP/result
$TESTPATH/usr/sbin/ufw  LOGGING OFF >> $TESTTMP/result 2>&1 || exit 1

echo "TESTING ARGS (enable/disable)" >> $TESTTMP/result || exit 1
echo "5" >> $TESTTMP/result
$TESTPATH/usr/sbin/ufw  enable >> $TESTTMP/result 2>&1 || exit 1
echo "6" >> $TESTTMP/result
$TESTPATH/usr/sbin/ufw  disable >> $TESTTMP/result 2>&1 || exit 1
echo "7" >> $TESTTMP/result
$TESTPATH/usr/sbin/ufw  ENABLE >> $TESTTMP/result 2>&1 || exit 1
echo "8" >> $TESTTMP/result
$TESTPATH/usr/sbin/ufw  DISABLE >> $TESTTMP/result 2>&1 || exit 1

echo "TESTING ARGS (allow/deny port)" >> $TESTTMP/result || exit 1
$TESTPATH/usr/sbin/ufw  allow 25 >> $TESTTMP/result 2>&1 || exit 1
echo "9" >> $TESTTMP/result
$TESTPATH/usr/sbin/ufw  deny 25 >> $TESTTMP/result 2>&1 || exit 1
echo "10" >> $TESTTMP/result
$TESTPATH/usr/sbin/ufw  deny 1 >> $TESTTMP/result 2>&1 || exit 1
echo "11" >> $TESTTMP/result
$TESTPATH/usr/sbin/ufw  deny 65535 >> $TESTTMP/result 2>&1 || exit 1

echo "TESTING ARGS (allow/deny to/from)" >> $TESTTMP/result || exit 1
echo "12" >> $TESTTMP/result
$TESTPATH/usr/sbin/ufw  allow 25 from 192.168.0.1 to 192.168.0.2 >> $TESTTMP/result 2>&1 || exit 1
$TESTPATH/usr/sbin/ufw  deny 25 from 192.168.0.1 to 192.168.0.2 >> $TESTTMP/result 2>&1 || exit 1
echo "13" >> $TESTTMP/result
$TESTPATH/usr/sbin/ufw  allow 25 from 192.168.0.1 >> $TESTTMP/result 2>&1 || exit 1
$TESTPATH/usr/sbin/ufw  deny 25 from 192.168.0.1 >> $TESTTMP/result 2>&1 || exit 1
echo "14" >> $TESTTMP/result
$TESTPATH/usr/sbin/ufw  allow 25 to 192.168.0.2 >> $TESTTMP/result 2>&1 || exit 1
$TESTPATH/usr/sbin/ufw  deny 25 to 192.168.0.2 >> $TESTTMP/result 2>&1 || exit 1

echo "15" >> $TESTTMP/result
$TESTPATH/usr/sbin/ufw  allow 25 to 192.168.0.0/24 >> $TESTTMP/result 2>&1 || exit 1
$TESTPATH/usr/sbin/ufw  deny 25 to 192.168.0.0/24 >> $TESTTMP/result 2>&1 || exit 1
echo "16" >> $TESTTMP/result
$TESTPATH/usr/sbin/ufw  allow 25 to 192.168.0.0/32 >> $TESTTMP/result 2>&1 || exit 1
$TESTPATH/usr/sbin/ufw  deny 25 to 192.168.0.0/32 >> $TESTTMP/result 2>&1 || exit 1
echo "17" >> $TESTTMP/result
$TESTPATH/usr/sbin/ufw  allow 25 to 192.168.0.0/12 >> $TESTTMP/result 2>&1 || exit 1
$TESTPATH/usr/sbin/ufw  deny 25 to 192.168.0.0/12 >> $TESTTMP/result 2>&1 || exit 1
echo "18" >> $TESTTMP/result
$TESTPATH/usr/sbin/ufw  allow 25 to 0.0.0.0/0 >> $TESTTMP/result 2>&1 || exit 1
$TESTPATH/usr/sbin/ufw  deny 25 to 0.0.0.0/0 >> $TESTTMP/result 2>&1 || exit 1

echo "TESTING ARGS (status)" >> $TESTTMP/result || exit 1
echo "19" >> $TESTTMP/result
$TESTPATH/usr/sbin/ufw  status >> $TESTTMP/result 2>&1 || exit 1

exit 0
