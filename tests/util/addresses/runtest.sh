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

let count=0
do_cmd() {
        if [ "$1" = "0" ] || [ "$1" = "1" ]; then
                expected="$1"
                shift
        fi

        cmd_results_file="$TESTTMP/result"
        if [ "$1" = "null" ]; then
                cmd_results_file="/dev/null"
                shift
        fi

        echo "$count: $@" >> $TESTTMP/result
        $script $@ >> $cmd_results_file 2>&1
        rc="$?"
        if [ "$rc" != "$expected" ]; then
                echo "Command '$@' exited with '$rc', but expected '$expected'"
                exit 1
        fi
        let count=count+1
        echo "" >> $TESTTMP/result
        echo "" >> $TESTTMP/result
}

# if running manually, do:
# cd tests/testarea
# PYTHONPATH="`pwd`/lib/python" python ./test_util.py ...
script="tests/testarea/test_addresses.py"
cat > $script << EOM
#!/usr/bin/python

import sys
import ufw.util

if len(sys.argv) != 3:
    print >> sys.stderr, "Wrong number of args: %d" % (len(sys.argv))
    sys.exit(1)
if not ufw.util.valid_address(sys.argv[2], sys.argv[1]):
    print >> sys.stderr, "Bad address: %s" % (sys.argv[2])
    sys.exit(1)
sys.exit(0)
EOM
chmod 755 $script

echo "BAD ADDRESSES" >> $TESTTMP/result
for version in 4 any; do
    for b in 16a 33 -1; do
        do_cmd "1"  $version 192.168.0.1/$b
    done
    for b in 256 s55 -1; do
        do_cmd "1" $version 192.168.0.$b
        do_cmd "1" $version 192.168.$b.1
        do_cmd "1" $version 192.$b.0.1
        do_cmd "1" $version $b.168.0.1
        do_cmd "1" $version 192.168.0.$b
        do_cmd "1" $version $b.$b.$b.$b
        do_cmd "1" $version 192.168.0.1/255.255.255.$b
        do_cmd "1" $version 192.168.0.1/255.255.$b.255
        do_cmd "1" $version 192.168.0.1/255.$b.255.255
        do_cmd "1" $version 192.168.0.1/$b.255.255.255
        do_cmd "1" $version 192.168.0.1/$b.$b.$b.$b
        do_cmd "1" $version $b.168.0.1/255.255.255.$b
        do_cmd "1" $version 192.$b.0.1/255.255.$b.255
        do_cmd "1" $version 192.168.$b.1/255.$b.255.255
        do_cmd "1" $version 192.168.0.$b/$b.255.255.255
        do_cmd "1" $version $b.$b.$b.$b/$b.$b.$b.$b
    done
done
for b in 129 s55 -1; do
    do_cmd "1" 6 ::1/$b
done


echo "VALID ADDRESSES" >> $TESTTMP/result
for version in 4 any; do
    do_cmd "0" $version 0.0.0.0
    do_cmd "0" $version 0.0.0.0/0
    do_cmd "0" $version 0.0.0.0/0.0.0.0
    do_cmd "0" $version 10.0.0.1
    do_cmd "0" $version 10.0.0.1/32
    do_cmd "0" $version 10.0.0.1/255.255.255.255
    for i in $(seq 0 32); do
        do_cmd "0" $version 192.168.0.1/$i
    done
    for i in $(seq 0 255); do
        do_cmd "0" $version 192.168.0.1/255.255.255.$i
        do_cmd "0" $version 192.168.0.1/255.255.$i.255
        do_cmd "0" $version 192.168.0.1/255.$i.255.255
        do_cmd "0" $version 192.168.0.1/$i.255.255.255
        do_cmd "0" $version 192.168.0.1/$i.$i.$i.$i
    done
done
for i in $(seq 0 128); do
    do_cmd "0" 6 ::1/$i
done

exit 0
