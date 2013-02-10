#
# Copyright 2012 Canonical Ltd.
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

import os
import unittest
import tests.unit.support
import ufw.applications

class ApplicationsTestCase(unittest.TestCase):
    def setUp(self):
        apps = os.path.join(ufw.common.config_dir, "applications.d")
        self.profiles = ufw.applications.get_profiles(apps)

    def tearDown(self):
        pass

    def test_get_profiles(self):
        '''Test get_profiles()'''
        try:
            ufw.applications.get_profiles("foo")
            self.assertFalse(True)
        except ufw.common.UFWError:
            pass

        self.assertTrue('WWW' in self.profiles.keys(), "Could not find 'WWW'")
        self.assertEquals(self.profiles['WWW']['ports'], "80/tcp")
        self.assertEquals(self.profiles['WWW']['title'], "Web Server")
        self.assertEquals(self.profiles['WWW']['description'], "Web server")

    def test_valid_profile_name(self):
        '''Test valid_profile_name()'''
        self.assertTrue(ufw.applications.valid_profile_name('ABC'))
        self.assertFalse(ufw.applications.valid_profile_name('#ABC'))
        self.assertFalse(ufw.applications.valid_profile_name('all'))
        self.assertFalse(ufw.applications.valid_profile_name('123'))
        self.assertFalse(ufw.applications.valid_profile_name('AB*C'))

    def test_verify_profile(self):
        '''Test verify_profile()'''
        self.assertTrue(ufw.applications.verify_profile('WWW',
            self.profiles['WWW']))
        print("TODO: verify bad profile")

    def test_get_title(self):
        '''Test get_title()'''
        self.assertEquals(ufw.applications.get_title(self.profiles['WWW']),
                'Web Server')

    def test_get_description(self):
        '''Test get_description()'''
        self.assertEquals(ufw.applications.get_description(self.profiles['WWW']),
                'Web server')

    def test_get_ports(self):
        '''Test get_ports()'''
        expected_ports = ['80/tcp']
        self.assertEquals(ufw.applications.get_ports(self.profiles['WWW']),
                expected_ports)

def test_main(): # used by runner.py
    tests.unit.support.run_unittest(
            ApplicationsTestCase
    )

if __name__ == "__main__": # used when standalone
    unittest.main()
