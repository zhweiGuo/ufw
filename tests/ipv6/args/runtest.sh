#!/bin/bash

#    Copyright (C) 2008 Canonical Ltd.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License version 3,
#    as published by the Free Software Foundation.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

sed -i 's/IPV6=no/IPV6=yes/' $TESTPATH/etc/default/ufw
sed -i 's/disableChecks = False/disableChecks = True/' $TESTPATH/usr/sbin/ufw

echo "TESTING ARGS (enable/disable)" >> $TESTTMP/result || exit 1
$TESTPATH/usr/sbin/ufw --dry-run enable >> $TESTTMP/result 2>&1 || exit 1
$TESTPATH/usr/sbin/ufw --dry-run disable >> $TESTTMP/result 2>&1 || exit 1

echo "TESTING ARGS (status)" >> $TESTTMP/result || exit 1
$TESTPATH/usr/sbin/ufw --dry-run status >> $TESTTMP/result 2>&1 || exit 1

exit 0
