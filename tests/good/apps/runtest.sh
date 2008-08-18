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

echo "TESTING APPLICATION INTEGRATION (args)" >> $TESTTMP/result
do_cmd "0" app list
do_cmd "0" app info Apache
do_cmd "0" app info 'Apache Secure'
do_cmd "0" app info 'Apache Full'
do_cmd "0" app info Bind9
do_cmd "0" app info Samba
do_cmd "0" app info 'Custom Web App'
do_cmd "0" app info all

echo "TESTING APPLICATION INTEGRATION (simple rules)" >> $TESTTMP/result
for target in allow deny limit ; do
    do_cmd "0" --dry-run $target Apache
    do_cmd "0" --dry-run $target 'Apache Secure'
    do_cmd "0" --dry-run $target 'Apache Full'
    do_cmd "0" --dry-run $target Bind9
    do_cmd "0" --dry-run $target Samba
    do_cmd "0" --dry-run $target OpenNTPD
    do_cmd "0" --dry-run $target 'Multi TCP'
    do_cmd "0" --dry-run $target 'Multi UDP'
done

echo "TESTING APPLICATION INTEGRATION (extended rules)" >> $TESTTMP/result
for target in allow deny limit ; do
    for i in to from ; do
        for loc in 192.168.0.0/16 any ; do
            do_cmd "0" --dry-run $target $i $loc app Apache
            do_cmd "0" --dry-run $target $i $loc app 'Apache Secure'
            do_cmd "0" --dry-run $target $i $loc app 'Apache Full'
            do_cmd "0" --dry-run $target $i $loc app Bind9
            do_cmd "0" --dry-run $target $i $loc app Samba
            do_cmd "0" --dry-run $target $i $loc app OpenNTPD
            do_cmd "0" --dry-run $target $i $loc app 'Multi TCP'
            do_cmd "0" --dry-run $target $i $loc app 'Multi UDP'
        done
    done

    for i in 192.168.0 any; do
        for j in from to; do
            k="to"
            if [ "$j" = "to" ]; then
                k="from"
            fi
            m="$i.1"
            n="$i.2"
            if [ "$i" = "any" ]; then
                m="$i"
                n="$i"
            fi
            do_cmd "0" --dry-run $target $j $m app Apache $k $n port 8080
            do_cmd "0" --dry-run $target $j $m app OpenNTPD $k $n port 10123
            do_cmd "0" --dry-run $target $j $m app Samba $k $n app Bind9
            do_cmd "0" --dry-run $target $j $m app Samba $k $n port 22
            do_cmd "0" --dry-run $target $j $m app Apache $k $n app 'Apache Full'
        done
        if [ "$i" != "any" ]; then
            i="$i.1"
        fi
        do_cmd "0" --dry-run $target to $i app Samba from $i app Samba
    done
done

# this is for live rules
echo "TESTING APPLICATION INTEGRATION (changed profile)" >> $TESTTMP/result
cat > $TESTPATH/etc/ufw/applications.d/runtest << EOM
[runtest]
title=runtest title
description=runtest description
ports=23/tcp
EOM
do_cmd "0" --dry-run allow runtest
rm -f $TESTPATH/etc/ufw/applications.d/runtest
do_cmd "0" --dry-run delete allow runtest


exit 0