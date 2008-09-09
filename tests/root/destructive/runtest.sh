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

echo "These tests are destructive and should only be run in a virtual machine"
echo -n "Continue (y|N)? "
read ans
if [ "$ans" = "y" ] || [ "$ans" = "Y" ]; then
    echo "Continuing with destructive tests..."
else
    echo "Skipping descructive tests"
    exit 0
fi

trap "/sbin/iptables.bak /sbin/iptables" EXIT HUP INT QUIT TERM
echo "Bug #262451 (part 2)" >> $TESTTMP/result
do_cmd "0"  disable
mv /sbin/iptables /sbin/iptables.bak || true
do_cmd "1"  enable
do_cmd "0"  status
mv /sbin/iptables.bak /sbin/iptables
trap - EXIT HUP INT QUIT TERM

trap "mount /proc" EXIT HUP INT QUIT TERM
echo "Bug #268084" >> $TESTTMP/result
do_cmd "0"  disable
umount /proc
do_cmd "1"  enable
do_cmd "0"  status
mount /proc
trap - EXIT HUP INT QUIT TERM

# teardown
do_cmd "0"  disable

exit 0
