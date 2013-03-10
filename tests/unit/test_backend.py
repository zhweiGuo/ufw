#
# Copyright 2012-2013 Canonical Ltd.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3,
# as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import unittest
import tests.unit.support
import ufw.backend
import ufw.backend_iptables
import ufw.common

class BackendTestCase(unittest.TestCase):
    def setUp(self):
        ufw.common.do_checks = False
        # ufw.backend is an interface, so to test it we need to instantiate
        # an object that implements this interface
        self.backend = ufw.backend_iptables.UFWBackendIptables(dryrun=True)

    def tearDown(self):
        pass

    def test_find_application_name(self):
        '''Test find_application_name()'''
        self.backend.find_application_name("WWW")

def test_main(): # used by runner.py
    tests.unit.support.run_unittest(
            BackendTestCase
    )

if __name__ == "__main__": # used when standalone
    unittest.main()
