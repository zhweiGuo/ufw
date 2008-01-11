#!/bin/bash

sed -i 's/disableChecks = False/disableChecks = True/' $TESTPATH/usr/sbin/ufw

echo "TESTING ARGS (logging)" >> $TESTTMP/result || exit 1
# bad
echo "1" >> $TESTTMP/result
$TESTPATH/usr/sbin/ufw --dry-run logging > /dev/null 2>&1 && exit 1
echo "2" >> $TESTTMP/result
$TESTPATH/usr/sbin/ufw --dry-run logging foo > /dev/null 2>&1 && exit 1
echo "3" >> $TESTTMP/result
$TESTPATH/usr/sbin/ufw --dry-run loggin on > /dev/null 2>&1 && exit 1
# good
echo "4" >> $TESTTMP/result
$TESTPATH/usr/sbin/ufw --dry-run logging on >> $TESTTMP/result 2>&1 || exit 1
echo "5" >> $TESTTMP/result
$TESTPATH/usr/sbin/ufw --dry-run logging off >> $TESTTMP/result 2>&1 || exit 1
echo "6" >> $TESTTMP/result
$TESTPATH/usr/sbin/ufw --dry-run LOGGING ON >> $TESTTMP/result 2>&1 || exit 1
echo "7" >> $TESTTMP/result
$TESTPATH/usr/sbin/ufw --dry-run LOGGING OFF >> $TESTTMP/result 2>&1 || exit 1

echo "TESTING ARGS (enable/disable)" >> $TESTTMP/result || exit 1
# bad
echo "8" >> $TESTTMP/result
$TESTPATH/usr/sbin/ufw --dry-run enabled > /dev/null 2>&1 && exit 1
echo "9" >> $TESTTMP/result
$TESTPATH/usr/sbin/ufw --dry-run disabled > /dev/null 2>&1 && exit 1

# good
echo "10" >> $TESTTMP/result
$TESTPATH/usr/sbin/ufw --dry-run enable >> $TESTTMP/result 2>&1 || exit 1
echo "11" >> $TESTTMP/result
$TESTPATH/usr/sbin/ufw --dry-run disable >> $TESTTMP/result 2>&1 || exit 1
echo "12" >> $TESTTMP/result
$TESTPATH/usr/sbin/ufw --dry-run ENABLE >> $TESTTMP/result 2>&1 || exit 1
echo "13" >> $TESTTMP/result
$TESTPATH/usr/sbin/ufw --dry-run DISABLE >> $TESTTMP/result 2>&1 || exit 1

echo "TESTING ARGS (allow/deny)" >> $TESTTMP/result || exit 1
echo "14" >> $TESTTMP/result
$TESTPATH/usr/sbin/ufw --dry-run allow > /dev/null 2>&1 && exit 1
echo "15" >> $TESTTMP/result
$TESTPATH/usr/sbin/ufw --dry-run deny > /dev/null 2>&1 && exit 1

echo "TESTING ARGS (allow/deny bad port)" >> $TESTTMP/result || exit 1
$TESTPATH/usr/sbin/ufw --dry-run alow 25 > /dev/null 2>&1 && exit 1
echo "16" >> $TESTTMP/result
$TESTPATH/usr/sbin/ufw --dry-run dny 25 > /dev/null 2>&1 && exit 1
echo "17" >> $TESTTMP/result
$TESTPATH/usr/sbin/ufw --dry-run allow 25a > /dev/null 2>&1 && exit 1
echo "18" >> $TESTTMP/result
$TESTPATH/usr/sbin/ufw --dry-run deny 25a > /dev/null 2>&1 && exit 1
echo "19" >> $TESTTMP/result
$TESTPATH/usr/sbin/ufw --dry-run allow 65536 > /dev/null 2>&1 && exit 1
echo "20" >> $TESTTMP/result
$TESTPATH/usr/sbin/ufw --dry-run deny 65536 > /dev/null 2>&1 && exit 1
echo "21" >> $TESTTMP/result
$TESTPATH/usr/sbin/ufw --dry-run allow 0 > /dev/null 2>&1 && exit 1
echo "22" >> $TESTTMP/result
$TESTPATH/usr/sbin/ufw --dry-run deny 0 > /dev/null 2>&1 && exit 1

echo "TESTING ARGS (allow/deny bad to/from)" >> $TESTTMP/result || exit 1
echo "23" >> $TESTTMP/result
$TESTPATH/usr/sbin/ufw --dry-run allow 25 to > /dev/null 2>&1 && exit 1
echo "24" >> $TESTTMP/result
$TESTPATH/usr/sbin/ufw --dry-run deny 25 to > /dev/null 2>&1 && exit 1
echo "25" >> $TESTTMP/result
$TESTPATH/usr/sbin/ufw --dry-run allow 25 from > /dev/null 2>&1 && exit 1
echo "26" >> $TESTTMP/result
$TESTPATH/usr/sbin/ufw --dry-run deny 25 from > /dev/null 2>&1 && exit 1
echo "27" >> $TESTTMP/result
$TESTPATH/usr/sbin/ufw --dry-run allow 25 from 192.168.0.1 to > /dev/null 2>&1 && exit 1
echo "28" >> $TESTTMP/result
$TESTPATH/usr/sbin/ufw --dry-run deny 25 from 192.168.0.1 to > /dev/null 2>&1 && exit 1
echo "29" >> $TESTTMP/result
$TESTPATH/usr/sbin/ufw --dry-run allow 25 from 192.168.0.1 from > /dev/null 2>&1 && exit 1
echo "30" >> $TESTTMP/result
$TESTPATH/usr/sbin/ufw --dry-run deny 25 from 192.168.0.1 from > /dev/null 2>&1 && exit 1
echo "31" >> $TESTTMP/result
$TESTPATH/usr/sbin/ufw --dry-run allow 25 to 192.168.0.1 from > /dev/null 2>&1 && exit 1
echo "32" >> $TESTTMP/result
$TESTPATH/usr/sbin/ufw --dry-run deny 25 to 192.168.0.1 from > /dev/null 2>&1 && exit 1
echo "33" >> $TESTTMP/result
$TESTPATH/usr/sbin/ufw --dry-run allow 25 to 192.168.0.1 to > /dev/null 2>&1 && exit 1
echo "34" >> $TESTTMP/result
$TESTPATH/usr/sbin/ufw --dry-run deny 25 to 192.168.0.1 to > /dev/null 2>&1 && exit 1
echo "35" >> $TESTTMP/result
$TESTPATH/usr/sbin/ufw --dry-run allow 25 to from 192.168.0.1 > /dev/null 2>&1 && exit 1
echo "36" >> $TESTTMP/result
$TESTPATH/usr/sbin/ufw --dry-run deny 25 to from 192.168.0.1 > /dev/null 2>&1 && exit 1
echo "37" >> $TESTTMP/result
$TESTPATH/usr/sbin/ufw --dry-run allow 25 from to 192.168.0.1 > /dev/null 2>&1 && exit 1
echo "38" >> $TESTTMP/result
$TESTPATH/usr/sbin/ufw --dry-run deny 25 from to 192.168.0.1 > /dev/null 2>&1 && exit 1
echo "39" >> $TESTTMP/result
$TESTPATH/usr/sbin/ufw --dry-run allow 25 from from 192.168.0.1 > /dev/null 2>&1 && exit 1
echo "40" >> $TESTTMP/result
$TESTPATH/usr/sbin/ufw --dry-run deny 25 from from 192.168.0.1 > /dev/null 2>&1 && exit 1
echo "41" >> $TESTTMP/result
$TESTPATH/usr/sbin/ufw --dry-run allow 25 to to 192.168.0.1 > /dev/null 2>&1 && exit 1
echo "42" >> $TESTTMP/result
$TESTPATH/usr/sbin/ufw --dry-run deny 25 to to 192.168.0.1 > /dev/null 2>&1 && exit 1

echo "TESTING ARGS (allow/deny bad ip)" >> $TESTTMP/result || exit 1
echo "43" >> $TESTTMP/result
$TESTPATH/usr/sbin/ufw --dry-run allow 25 to 192.168.0. >> $TESTTMP/result 2>&1 && exit 1
echo "44" >> $TESTTMP/result
$TESTPATH/usr/sbin/ufw --dry-run allow 25 to 192.168.0.1.1 >> $TESTTMP/result 2>&1 && exit 1
echo "45" >> $TESTTMP/result
$TESTPATH/usr/sbin/ufw --dry-run allow 25 to foo >> $TESTTMP/result 2>&1 && exit 1
echo "46" >> $TESTTMP/result
$TESTPATH/usr/sbin/ufw --dry-run allow 25 to xxx.xxx.xxx.xx >> $TESTTMP/result 2>&1 && exit 1
echo "47" >> $TESTTMP/result
$TESTPATH/usr/sbin/ufw --dry-run allow 25 to 192a.168.0.1 >> $TESTTMP/result 2>&1 && exit 1
echo "48" >> $TESTTMP/result
$TESTPATH/usr/sbin/ufw --dry-run allow 25 to 192.168a.0.1 >> $TESTTMP/result 2>&1 && exit 1
echo "49" >> $TESTTMP/result
$TESTPATH/usr/sbin/ufw --dry-run allow 25 to 192.168.0a.1 >> $TESTTMP/result 2>&1 && exit 1
echo "50" >> $TESTTMP/result
$TESTPATH/usr/sbin/ufw --dry-run allow 25 to 192.168.1.a1 >> $TESTTMP/result 2>&1 && exit 1
echo "51" >> $TESTTMP/result
$TESTPATH/usr/sbin/ufw --dry-run allow 25 to 192.168.1..1 >> $TESTTMP/result 2>&1 && exit 1
echo "52" >> $TESTTMP/result
$TESTPATH/usr/sbin/ufw --dry-run allow 25 to 192.168.1..1/24 >> $TESTTMP/result 2>&1 && exit 1
echo "53" >> $TESTTMP/result
$TESTPATH/usr/sbin/ufw --dry-run allow 25 to 192.168.1.256 >> $TESTTMP/result 2>&1 && exit 1
echo "54" >> $TESTTMP/result
$TESTPATH/usr/sbin/ufw --dry-run allow 25 to 256.0.0.0 >> $TESTTMP/result 2>&1 && exit 1
echo "55" >> $TESTTMP/result
$TESTPATH/usr/sbin/ufw --dry-run allow 25 to 10.256.0.0 >> $TESTTMP/result 2>&1 && exit 1


exit 0
