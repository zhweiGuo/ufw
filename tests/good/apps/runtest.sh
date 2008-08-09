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

