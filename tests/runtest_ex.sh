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

#set -x

# disable checks for test run
#sed -i 's/disable_checks = False/disable_checks = True/' $TESTPATH/usr/sbin/ufw

# example usage for successful run
#$TESTPATH/usr/sbin/ufw help >> $TESTTMP/result 2>&1 || exit 1

# example usage for failed run
#$TESTPATH/usr/sbin/ufw logging >> $TESTTMP/result 2>&1 && exit 1

# remove this when implementing real test
touch $TESTTMP/result || exit 1

exit 0

