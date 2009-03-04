#!/bin/bash

#    Copyright (C) 2009 Canonical Ltd.
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

echo "Bug #319226" >> $TESTTMP/result
mkdir $TESTPATH/etc/ufw/applications.d/.svn
touch $TESTPATH/etc/ufw/applications.d/.hgignore
cat > $TESTPATH/etc/ufw/applications.d/.testme << EOM
[Bug319226]
title=test 319226
description=test description
ports=23/tcp
EOM
do_cmd "0" app list

echo "Bug #337705" >> $TESTTMP/result
sed -i 's/import ufw.frontend/import ufw.nonexistent/' $TESTPATH/usr/sbin/ufw
do_cmd "1" help
sed -i 's/import ufw.nonexistent/import ufw.frontend/' $TESTPATH/usr/sbin/ufw


exit 0
