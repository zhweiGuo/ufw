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

echo "TESTING ARGS (logging)" >> $TESTTMP/result
do_cmd "1" null --dry-run logging
do_cmd "1" null --dry-run logging foo
do_cmd "1" null --dry-run loggin on

echo "TESTING ARGS (default)" >> $TESTTMP/result
do_cmd "1" null --dry-run default
do_cmd "1" null --dry-run default foo
do_cmd "1" null --dry-run default accept
do_cmd "1" null --dry-run defaul allow

echo "TESTING ARGS (enable/disable)" >> $TESTTMP/result
# bad
do_cmd "1" null --dry-run enabled
do_cmd "1" null --dry-run disabled

echo "TESTING ARGS (allow/deny)" >> $TESTTMP/result
do_cmd "1" null --dry-run allow
do_cmd "1" null --dry-run deny

echo "TESTING ARGS (allow/deny bad port)" >> $TESTTMP/result
do_cmd "1" null --dry-run alow 25
do_cmd "1" null --dry-run dny 25
do_cmd "1" null --dry-run allow 25a
do_cmd "1" null --dry-run deny 25a
do_cmd "1" null --dry-run allow 65536
do_cmd "1" null --dry-run deny 65536
do_cmd "1" null --dry-run allow 0
do_cmd "1" null --dry-run deny 0
do_cmd "1" null --dry-run deny XXX

echo "TESTING ARGS (allow/deny bad to/from)" >> $TESTTMP/result
do_cmd "1" null --dry-run allow 25 to
do_cmd "1" null --dry-run deny 25 to
do_cmd "1" null --dry-run allow 25 from
do_cmd "1" null --dry-run deny 25 from
do_cmd "1" null --dry-run allow 25 from 192.168.0.1 to
do_cmd "1" null --dry-run deny 25 from 192.168.0.1 to
do_cmd "1" null --dry-run allow 25 from 192.168.0.1 from
do_cmd "1" null --dry-run deny 25 from 192.168.0.1 from
do_cmd "1" null --dry-run allow 25 to 192.168.0.1 from
do_cmd "1" null --dry-run deny 25 to 192.168.0.1 from
do_cmd "1" null --dry-run allow 25 to 192.168.0.1 to
do_cmd "1" null --dry-run deny 25 to 192.168.0.1 to
do_cmd "1" null --dry-run allow 25 to from 192.168.0.1
do_cmd "1" null --dry-run deny 25 to from 192.168.0.1
do_cmd "1" null --dry-run allow 25 from to 192.168.0.1
do_cmd "1" null --dry-run deny 25 from to 192.168.0.1
do_cmd "1" null --dry-run allow 25 from from 192.168.0.1
do_cmd "1" null --dry-run deny 25 from from 192.168.0.1
do_cmd "1" null --dry-run allow 25 to to 192.168.0.1
do_cmd "1" null --dry-run deny 25 to to 192.168.0.1

echo "TESTING ARGS (allow/deny bad ip)" >> $TESTTMP/result
do_cmd "1" null --dry-run allow 25 to 192.168.0.
do_cmd "1" null --dry-run allow 25 to 192.168.0.1.1
do_cmd "1" null --dry-run allow 25 to foo
do_cmd "1" null --dry-run allow 25 to xxx.xxx.xxx.xx
do_cmd "1" null --dry-run allow 25 to 192a.168.0.1
do_cmd "1" null --dry-run allow 25 to 192.168a.0.1
do_cmd "1" null --dry-run allow 25 to 192.168.0a.1
do_cmd "1" null --dry-run allow 25 to 192.168.1.a1
do_cmd "1" null --dry-run allow 25 to 192.168.1..1
do_cmd "1" null --dry-run allow 25 to 192.168.1..1/24
do_cmd "1" null --dry-run allow 25 to 192.168.1.256
do_cmd "1" null --dry-run allow 25 to 256.0.0.0
do_cmd "1" null --dry-run allow 25 to 10.256.0.0

echo "TESTING ARGS (delete allow/deny)" >> $TESTTMP/result
do_cmd "1" null --dry-run delete


exit 0
