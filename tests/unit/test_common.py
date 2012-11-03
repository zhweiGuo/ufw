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

import unittest
import tests.unit.support
import src.common as common

class CommonTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_ufwerror(self):
        '''Test UFWError'''
        try:
            raise common.UFWError("test")
        except common.UFWError as e:
            self.assertEquals(e.value, "test", "'%s' != 'test'" % e.value)
            return
        self.assertTrue(False, "Did not raise an error")

    def test___init__(self):
        '''TODO: Test __init__()'''

    def test___str__(self):
        '''TODO: Test __str__()'''

    def test__get_attrib(self):
        '''TODO: Test _get_attrib()'''

    def test_dup_rule(self):
        '''TODO: Test dup_rule()'''

    def test_format_rule(self):
        '''TODO: Test format_rule()'''

    def test_set_action(self):
        '''TODO: Test set_action()'''

    def test_set_port(self):
        '''TODO: Test set_port()'''

    def test_set_protocol(self):
        '''TODO: Test set_protocol()'''

    def test__fix_anywhere(self):
        '''TODO: Test _fix_anywhere()'''

    def test_set_v6(self):
        '''TODO: Test set_v6()'''

    def test_set_src(self):
        '''TODO: Test set_src()'''

    def test_set_dst(self):
        '''TODO: Test set_dst()'''

    def test_set_interface(self):
        '''TODO: Test set_interface()'''

    def test_set_position(self):
        '''TODO: Test set_position()'''

    def test_set_logtype(self):
        '''TODO: Test set_logtype()'''

    def test_set_direction(self):
        '''TODO: Test set_direction()'''

    def test_normalize(self):
        '''TODO: Test normalize()'''

    def test_match(self):
        '''TODO: Test match()'''

    def test_fuzzy_dst_match(self):
        '''TODO: Test fuzzy_dst_match()'''

    def test__match_ports(self):
        '''TODO: Test _match_ports()'''

    def test__is_anywhere(self):
        '''TODO: Test _is_anywhere()'''

    def test_get_app_tuple(self):
        '''TODO: Test get_app_tuple()'''


def test_main(): # used by runner.py
    tests.unit.support.run_unittest(
            CommonTestCase
    )

if __name__ == "__main__": # used when standalone
    unittest.main()
