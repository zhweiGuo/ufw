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

source "$TESTPATH/../testlib.sh"
cp $TESTPATH/../defaults/profiles.bad/* $TESTPATH/etc/ufw/applications.d

echo "TESTING BAD PROFILE (command name)" >> $TESTTMP/result
do_cmd "1" null --dry-run app info foo
do_cmd "1" null --dry-run app info Custom Web App

echo "TESTING BAD PROFILE (name)" >> $TESTTMP/result
do_cmd "1" null --dry-run app info bad-description1
do_cmd "1" null --dry-run app info bad-description2
do_cmd "1" null --dry-run app info bad-title1
do_cmd "1" null --dry-run app info bad-title2
do_cmd "1" null --dry-run app info bad-ports1
do_cmd "1" null --dry-run app info bad-ports2
do_cmd "1" null --dry-run app info bad-ports3
do_cmd "1" null --dry-run app info bad-ports4
do_cmd "1" null --dry-run app info bad-ports5
do_cmd "1" null --dry-run app info bad-ports6

exit 0
