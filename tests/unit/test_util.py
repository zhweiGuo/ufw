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
import ufw.util

import os
import socket
import tempfile

class UtilTestCase(unittest.TestCase):
    def setUp(self):
        self.tmpdir = None

    def tearDown(self):
        if self.tmpdir and os.path.isdir(self.tmpdir):
            tests.unit.support.recursive_rm(self.tmpdir)

    def test_get_services_proto(self):
        '''Test get_services_proto()'''
        res = ufw.util.get_services_proto("echo")
        self.assertTrue(res == "any", res)

        res = ufw.util.get_services_proto("tcpmux")
        self.assertTrue(res == "tcp", res)

        res = ufw.util.get_services_proto("fsp")
        self.assertTrue(res == "udp", res)

    def test_parse_port_proto(self):
        '''Test parse_port_proto()'''
        (s, p) = ufw.util.parse_port_proto("7")
        self.assertTrue(s == "7", s)
        self.assertTrue(p == "any", p)

        (s, p) = ufw.util.parse_port_proto("7/tcp")
        self.assertTrue(s == "7", s)
        self.assertTrue(p == "tcp", p)

        (s, p) = ufw.util.parse_port_proto("7/udp")
        self.assertTrue(s == "7", s)
        self.assertTrue(p == "udp", p)

    def test_valid_address6(self):
        '''Test valid_address6()'''
        if not socket.has_ipv6:
            return tests.unit.support.skipped(self, "ipv6 not enabled")

        bad = [
                ':::1',
                'fe80::-1',
                '000000000000000000000000000000000000000000000000001',
                '2001:db8:::/32',
                '2001:db8::/129',
                '2001:gb8::/32',
                '2001:db8:3:4:5:6:7:8:9',
                'foo',
                'xxx:xxx:xxx:xx:xxx:xxx:xxx:xxx',
                'g001:db8:3:4:5:6:7:8',
                '2001:gb8:3:4:5:6:7:8',
                '2001:db8:g:4:5:6:7:8',
                '2001:db8:3:g:5:6:7:8',
                '2001:db8:3:4:g:6:7:8',
                '2001:db8:3:4:5:g:7:8',
                '2001:db8:3:4:5:6:g:8',
                '2001:db8:3:4:5:6:7:g',
                '2001:0db8:0000:0000:0000:0000:0000:0000/129',
                '2001:0db8:0000:0000:0000:0000:0000:00000/128',
                '2001:0db8:0000:0000:0000:0000:0000:00000/12a',
              ]

        for b in bad:
            self.assertFalse(ufw.util.valid_address6(b), b)

        good = [
                '2001:db8::/32',
                '2001:db8:3:4:5:6:7:8',
                '2001:db8:85a3:8d3:1319:8a2e:370:734',
                '::1',
                '::1/0',
                '::1/32',
                '::1/128',
               ]

        for g in good:
            self.assertTrue(ufw.util.valid_address6(g), g)


    def test_valid_address4(self):
        '''Test valid_address4()'''
        bad = [
                '192.168.0.-1',
                '192.168.256.1',
                '192.s55.0.1',
                '.168.0.1',
                '2001:db8::/32',
                '2001:db8:3:4:5:6:7:8',
                '2001:db8:85a3:8d3:1319:8a2e:370:734',
              ]

        for b in bad:
            self.assertFalse(ufw.util.valid_address4(b), b)

        good = [
                '192.168.0.0',
                '192.168.0.1',
                '192.168.0.254',
                '192.168.0.255',
                '192.168.0.128',
                '192.168.1.128',
                '192.168.254.128',
                '192.168.255.128',
                '192.0.128.128',
                '192.1.128.128',
                '192.254.128.128',
                '192.255.128.128',
                '0.128.128.128',
                '1.128.128.128',
                '254.128.128.128',
                '255.128.128.128',
               ]

        for g in good:
            self.assertTrue(ufw.util.valid_address4(g), g)

    def test_valid_netmask(self):
        '''Test valid_netmask()'''

        # v4
        bad = [
               'a',
               '-1',
               '33',
              ]

        for b in bad:
            self.assertFalse(ufw.util.valid_netmask(b, v6=False), b)

        good = [
                '0',
                '1',
                '16',
                '31',
                '32',
                '255.255.255.0',
                '255.255.128.0',
                '255.64.255.0',
                '32.255.255.0',
               ]

        for g in good:
            self.assertTrue(ufw.util.valid_netmask(g, v6=False), g)


        # v6
        bad = [
               '129',
               '12a',
               'a',
               '-1',
              ]

        for b in bad:
            self.assertFalse(ufw.util.valid_netmask(b, v6=True), b)

        good = [
                '0',
                '1',
                '31',
                '32',
                '33',
                '127',
                '128',
               ]

        for g in good:
            self.assertTrue(ufw.util.valid_netmask(g, v6=True), g)


    def test_valid_address(self):
        '''Test valid_address()'''
        bad = [
                ':::1',
                'fe80::-1',
                '192.168.0.-1',
                '192.168.256.1',
                '192.s55.0.1',
                '.168.0.1',
              ]

        for b in bad:
            self.assertFalse(ufw.util.valid_address(b, "any"), b)
            self.assertFalse(ufw.util.valid_address(b, "4"), b)
            self.assertFalse(ufw.util.valid_address(b, "6"), b)

        good = [
                '192.168.0.0',
                '192.168.0.1',
                '192.168.0.254',
                '192.168.0.255',
                '2001:db8::/32',
                '2001:db8:3:4:5:6:7:8',
                '2001:db8:85a3:8d3:1319:8a2e:370:734',
                '::1',
               ]

        for g in good:
            self.assertTrue(ufw.util.valid_address(g, "any"), g)
            if ':' in g:
                self.assertTrue(ufw.util.valid_address(g, "6"), g)
            else:
                self.assertTrue(ufw.util.valid_address(g, "4"), g)


    def test_normalize_address(self):
        '''TODO: Test normalize_address()'''

    def test_fileio(self):
        '''TODO: Test fileio helpers()'''
        self.tmpdir = tempfile.mkdtemp()
        tmp = os.path.join(self.tmpdir, "foo")
        f = open(tmp, 'w')
        f.close()

        f = ufw.util.open_file_read(tmp)
        f.close()

    def test_open_files(self):
        '''TODO: Test open_files()'''

    def test_write_to_file(self):
        '''TODO: Test write_to_file()'''

    def test_close_files(self):
        '''TODO: Test close_files()'''

    def test_cmd(self):
        '''TODO: Test cmd()'''

    def test_cmd_pipe(self):
        '''TODO: Test cmd_pipe()'''

    def test__print(self):
        '''TODO: Test _print()'''

    def test_error(self):
        '''TODO: Test error()'''

    def test_warn(self):
        '''TODO: Test warn()'''

    def test_msg(self):
        '''TODO: Test msg()'''

    def test_debug(self):
        '''TODO: Test debug()'''

    def test_word_wrap(self):
        '''TODO: Test word_wrap()'''

    def test_wrap_text(self):
        '''TODO: Test wrap_text()'''

    def test_human_sort(self):
        '''TODO: Test human_sort()'''

    def test_get_ppid(self):
        '''TODO: Test get_ppid()'''

    def test_under_ssh(self):
        '''TODO: Test under_ssh()'''

    def test__valid_cidr_netmask(self):
        '''TODO: Test _valid_cidr_netmask()'''

    def test__valid_dotted_quads(self):
        '''TODO: Test _valid_dotted_quads()'''

    def test__dotted_netmask_to_cidr(self):
        '''TODO: Test _dotted_netmask_to_cidr()'''

    def test__cidr_to_dotted_netmask(self):
        '''TODO: Test _cidr_to_dotted_netmask()'''

    def test__address4_to_network(self):
        '''TODO: Test _address4_to_network()'''

    def test__address6_to_network(self):
        '''TODO: Test _address6_to_network()'''

    def test_in_network(self):
        '''TODO: Test in_network()'''

    def test_get_iptables_version(self):
        '''TODO: Test get_iptables_version()'''

    def test_get_netfilter_capabilities(self):
        '''TODO: Test get_netfilter_capabilities()'''

    def test_parse_netstat_output(self):
        '''TODO: Test parse_netstat_output()'''

    def test_get_ip_from_if(self):
        '''TODO: Test get_ip_from_if()'''

    def test_get_if_from_ip(self):
        '''TODO: Test get_if_from_ip()'''

    def test__get_proc_inodes(self):
        '''TODO: Test _get_proc_inodes()'''

    def test__read_proc_net_protocol(self):
        '''TODO: Test _read_proc_net_protocol()'''

    def test_convert_proc_address(self):
        '''TODO: Test convert_proc_address()'''

    def test_get_netstat_output(self):
        '''TODO: Test get_netstat_output()'''


def test_main(): # used by runner.py
    tests.unit.support.run_unittest(
            UtilTestCase
    )

if __name__ == "__main__": # used when standalone
    unittest.main()
