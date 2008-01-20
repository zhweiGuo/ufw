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

sed -i 's/disable_checks = False/disable_checks = True/' $TESTPATH/usr/sbin/ufw

let count=0
do_cmd() {
        echo "$count: $@" >> $TESTTMP/result
        $TESTPATH/usr/sbin/ufw $@ >> $TESTTMP/result 2>&1 || exit 1
        let count=count+1
        echo "" >> $TESTTMP/result
        echo "" >> $TESTTMP/result
}

echo "TESTING ARGS (logging)" >> $TESTTMP/result
do_cmd --dry-run logging on 
do_cmd --dry-run logging off 
do_cmd --dry-run LOGGING ON 
do_cmd --dry-run LOGGING OFF 

echo "TESTING ARGS (default)" >> $TESTTMP/result
do_cmd --dry-run default allow
do_cmd --dry-run default deny
do_cmd --dry-run DEFAULT ALLOW
do_cmd --dry-run DEFAULT DENY

echo "TESTING ARGS (enable/disable)" >> $TESTTMP/result || exit 1
do_cmd --dry-run enable 
do_cmd --dry-run disable 
do_cmd --dry-run ENABLE 
do_cmd --dry-run DISABLE 

echo "TESTING ARGS (status)" >> $TESTTMP/result || exit 1
do_cmd --dry-run status

exit 0
