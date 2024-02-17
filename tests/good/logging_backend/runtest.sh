#!/bin/bash

#    Copyright 2009 Canonical Ltd.
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

source "$TESTPATH/../testlib.sh"
sed -i '/LOGGING_BACKEND/d' $TESTPATH/etc/default/ufw
echo "LOGGING_BACKEND=netfilter_log" >>$TESTPATH/etc/default/ufw

echo "TESTING NFLOG RULES" >> $TESTTMP/result
for i in allow deny limit reject ; do
    for j in log log-all ; do
        do_cmd "0" null $i $j 23
        do_cmd "0" null $i $j smtp
        do_cmd "0" null $i $j tftp
        do_cmd "0" null $i $j daytime
        do_cmd "0" null $i $j Samba
        do_cmd "0" null $i $j Apache
        do_cmd "0" null $i $j from 192.168.0.1 port smtp to 10.0.0.1 port smtp
        do_cmd "0" null $i $j from 192.168.0.1 app Samba to 10.0.0.1 app Samba

        echo "contents of user*.rules:" >> $TESTTMP/result
        cat $TESTCONFIG/user.rules >> $TESTTMP/result
        cat $TESTCONFIG/user6.rules >> $TESTTMP/result

        # now delete the rules
        do_cmd "0" null delete $i $j 23
        do_cmd "0" null delete $i $j smtp
        do_cmd "0" null delete $i $j tftp
        do_cmd "0" null delete $i $j daytime
        do_cmd "0" null delete $i $j Samba
        do_cmd "0" null delete $i $j Apache
        do_cmd "0" null delete $i $j from 192.168.0.1 port smtp to 10.0.0.1 port smtp
        do_cmd "0" null delete $i $j from 192.168.0.1 app Samba to 10.0.0.1 app Samba

        echo "contents of user*.rules:" >> $TESTTMP/result
        cat $TESTCONFIG/user.rules >> $TESTTMP/result
        cat $TESTCONFIG/user6.rules >> $TESTTMP/result
    done
done

exit 0
