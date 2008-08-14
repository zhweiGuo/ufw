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
do_cmd "1" null app info foo
do_cmd "1" null app info Custom Web App

echo "TESTING BAD PROFILE (name)" >> $TESTTMP/result
do_cmd "1" null app info bad-description1
do_cmd "1" null app info bad-description2
do_cmd "1" null app info bad-title1
do_cmd "1" null app info bad-title2
do_cmd "1" null app info bad-ports1
do_cmd "1" null app info bad-ports2
do_cmd "1" null app info bad-ports3
do_cmd "1" null app info bad-ports4
do_cmd "1" null app info bad-ports5
do_cmd "1" null app info bad-ports6

echo "TESTING APPLICATION INTEGRATION (bad simple rules)" >> $TESTTMP/result
for target in allow deny limit ; do
    do_cmd "1" null $target NONEXISTENT
    do_cmd "1" null $target Apache/tcp
done

echo "TESTING APPLICATION INTEGRATION (bad extended rules)" >> $TESTTMP/result
for target in allow deny limit ; do
    for i in to from ; do
        k="to"
        if [ "$i" = "to" ]; then
            k="from"
        fi
        for loc in 192.168.0.0/16 any ; do
            do_cmd "1" null --dry-run $target $i $loc app NONEXISTENT
            do_cmd "1" null --dry-run $target $i $loc app Apache proto tcp
            do_cmd "1" null --dry-run $target $i $loc app Apache proto udp
            do_cmd "1" null --dry-run $target $i $loc app 'No Protocol Multi'
            do_cmd "1" null --dry-run $target $i $loc app Samba $k $loc port http
            do_cmd "1" null --dry-run $target $i $loc app Samba $k $loc port 22 proto tcp
        done
    done
done

exit 0
