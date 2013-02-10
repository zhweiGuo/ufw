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


    def _run_normalize_address(self, data):
        '''Run ufw.util.normalize_address() on data. Data should be in form
           of:
           data = [(v6, ip, expected_ip), (v6, ip2, expected_ip2)]   
        '''
        error_str = ""
        for (v6, ip, expected) in data:
            res = ufw.util.normalize_address(ip, v6)[0]
            if expected != res:
                error_str += "'%s' != '%s' (v6=%s)\n" % (res, expected, v6)
        return error_str

    def test_normalize_address_host_netmask(self):
        '''Test normalize_address() with host_netmask'''
        data = [
                 (False, '192.168.0.1', '192.168.0.1'),
                 (False, '192.168.0.1/32', '192.168.0.1'),
                 (False, '192.168.0.1/255.255.255.255', '192.168.0.1'),
                 (True, '::1', '::1'),
                 (True, '::1/128' ,'::1'),
                ]

        error_str = self._run_normalize_address(data)
        self.assertEquals(error_str, "", error_str)

    def test_normalize_address_netmask_to_cidr(self):
        '''Test normalize_address() with netmask_to_cidr'''
        data = [
                 (False, '192.168.0.1/255.255.255.255', '192.168.0.1'),
                 (False, '192.168.0.0/255.255.255.254', '192.168.0.0/31'),
                 (False, '192.168.0.0/255.255.255.252', '192.168.0.0/30'),
                 (False, '192.168.0.0/255.255.255.248', '192.168.0.0/29'),
                 (False, '192.168.0.0/255.255.255.240', '192.168.0.0/28'),
                 (False, '192.168.0.0/255.255.255.224', '192.168.0.0/27'),
                 (False, '192.168.0.0/255.255.255.192', '192.168.0.0/26'),
                 (False, '192.168.0.0/255.255.255.128', '192.168.0.0/25'),
                 (False, '192.168.0.0/255.255.255.0', '192.168.0.0/24'),
                 (False, '192.168.0.0/255.255.254.0', '192.168.0.0/23'),
                 (False, '192.168.0.0/255.255.252.0', '192.168.0.0/22'),
                 (False, '192.168.0.0/255.255.248.0', '192.168.0.0/21'),
                 (False, '192.168.0.0/255.255.240.0', '192.168.0.0/20'),
                 (False, '192.168.0.0/255.255.224.0', '192.168.0.0/19'),
                 (False, '192.168.0.0/255.255.192.0', '192.168.0.0/18'),
                 (False, '192.168.0.0/255.255.128.0', '192.168.0.0/17'),
                 (False, '192.168.0.0/255.255.0.0', '192.168.0.0/16'),
                 (False, '192.168.0.0/255.254.0.0', '192.168.0.0/15'),
                 (False, '192.168.0.0/255.252.0.0', '192.168.0.0/14'),
                 (False, '192.168.0.0/255.248.0.0', '192.168.0.0/13'),
                 (False, '192.168.0.0/255.240.0.0', '192.160.0.0/12'),
                 (False, '192.168.0.0/255.224.0.0', '192.160.0.0/11'),
                 (False, '192.168.0.0/255.192.0.0', '192.128.0.0/10'),
                 (False, '192.168.0.0/255.128.0.0', '192.128.0.0/9'),
                 (False, '192.168.0.0/255.0.0.0', '192.0.0.0/8'),
                 (False, '192.168.0.0/254.0.0.0', '192.0.0.0/7'),
                 (False, '192.168.0.0/252.0.0.0', '192.0.0.0/6'),
                 (False, '192.168.0.0/248.0.0.0', '192.0.0.0/5'),
                 (False, '192.168.0.0/240.0.0.0', '192.0.0.0/4'),
                 (False, '192.168.0.0/224.0.0.0', '192.0.0.0/3'),
                 (False, '192.168.0.0/192.0.0.0', '192.0.0.0/2'),
                 (False, '192.168.0.0/128.0.0.0', '128.0.0.0/1'),
                ]

        error_str = self._run_normalize_address(data)
        self.assertEquals(error_str, "", error_str)
            
    def test_normalize_address_ipv6_cidr(self):
        '''Test normalize_address() with ipv6_cidr'''
        data = []
        for cidr in range(0, 128):
            data.append((True, '::1/%d' % cidr, '::1/%d' % cidr))
        error_str = self._run_normalize_address(data)
        self.assertEquals(error_str, "", error_str)

    def test_normalize_address_valid_netmask_to_non_cidr(self):
        '''Test normalize_address() with valid_netmask_to_non_cidr'''
        data = []

        cidrs = [252, 248, 240, 224, 192, 128]
        for i in range(1, 254):
            if i in cidrs:
                continue
            data.append((False, '192.168.0.0/255.255.255.%d' % i, '192.168.0.0/255.255.255.%d' % i))
            if i < 8:
                data.append((False, '192.168.0.0/255.%d.0.0' % i, '192.0.0.0/255.%d.0.0' % i))
            elif i < 16:
                data.append((False, '192.168.0.0/255.%d.0.0' % i, '192.8.0.0/255.%d.0.0' % i))
            elif i < 24:
                data.append((False, '192.168.0.0/255.%d.0.0' % i, '192.0.0.0/255.%d.0.0' % i))
            elif i < 32:
                data.append((False, '192.168.0.0/255.%d.0.0' % i, '192.8.0.0/255.%d.0.0' % i))
            elif i < 40:
                data.append((False, '192.168.0.0/255.%d.0.0' % i, '192.32.0.0/255.%d.0.0' % i))
            elif i < 48:
                data.append((False, '192.168.0.0/255.%d.0.0' % i, '192.40.0.0/255.%d.0.0' % i))
            elif i < 56:
                data.append((False, '192.168.0.0/255.%d.0.0' % i, '192.32.0.0/255.%d.0.0' % i))
            elif i < 64:
                data.append((False, '192.168.0.0/255.%d.0.0' % i, '192.40.0.0/255.%d.0.0' % i))
            elif i < 72:
                data.append((False, '192.168.0.0/255.%d.0.0' % i, '192.0.0.0/255.%d.0.0' % i))
            elif i < 80:
                data.append((False, '192.168.0.0/255.%d.0.0' % i, '192.8.0.0/255.%d.0.0' % i))
            elif i < 88:
                data.append((False, '192.168.0.0/255.%d.0.0' % i, '192.0.0.0/255.%d.0.0' % i))
            elif i < 96:
                data.append((False, '192.168.0.0/255.%d.0.0' % i, '192.8.0.0/255.%d.0.0' % i))
            elif i < 104:
                data.append((False, '192.168.0.0/255.%d.0.0' % i, '192.32.0.0/255.%d.0.0' % i))
            elif i < 112:
                data.append((False, '192.168.0.0/255.%d.0.0' % i, '192.40.0.0/255.%d.0.0' % i))
            elif i < 120:
                data.append((False, '192.168.0.0/255.%d.0.0' % i, '192.32.0.0/255.%d.0.0' % i))
            elif i < 128:
                data.append((False, '192.168.0.0/255.%d.0.0' % i, '192.40.0.0/255.%d.0.0' % i))
            elif i < 136:
                data.append((False, '192.168.0.0/255.%d.0.0' % i, '192.128.0.0/255.%d.0.0' % i))
            elif i < 144:
                data.append((False, '192.168.0.0/255.%d.0.0' % i, '192.136.0.0/255.%d.0.0' % i))
            elif i < 152:
                data.append((False, '192.168.0.0/255.%d.0.0' % i, '192.128.0.0/255.%d.0.0' % i))
            elif i < 160:
                data.append((False, '192.168.0.0/255.%d.0.0' % i, '192.136.0.0/255.%d.0.0' % i))
            elif i < 168:
                data.append((False, '192.168.0.0/255.%d.0.0' % i, '192.160.0.0/255.%d.0.0' % i))
            elif i < 176:
                data.append((False, '192.168.0.0/255.%d.0.0' % i, '192.168.0.0/255.%d.0.0' % i))
            elif i < 184:
                data.append((False, '192.168.0.0/255.%d.0.0' % i, '192.160.0.0/255.%d.0.0' % i))
            elif i < 192:
                data.append((False, '192.168.0.0/255.%d.0.0' % i, '192.168.0.0/255.%d.0.0' % i))
            elif i < 200:
                data.append((False, '192.168.0.0/255.%d.0.0' % i, '192.128.0.0/255.%d.0.0' % i))
            elif i < 208:
                data.append((False, '192.168.0.0/255.%d.0.0' % i, '192.136.0.0/255.%d.0.0' % i))
            elif i < 216:
                data.append((False, '192.168.0.0/255.%d.0.0' % i, '192.128.0.0/255.%d.0.0' % i))
            elif i < 224:
                data.append((False, '192.168.0.0/255.%d.0.0' % i, '192.136.0.0/255.%d.0.0' % i))
            elif i < 232:
                data.append((False, '192.168.0.0/255.%d.0.0' % i, '192.160.0.0/255.%d.0.0' % i))
            elif i < 240:
                data.append((False, '192.168.0.0/255.%d.0.0' % i, '192.168.0.0/255.%d.0.0' % i))
            elif i < 248:
                data.append((False, '192.168.0.0/255.%d.0.0' % i, '192.160.0.0/255.%d.0.0' % i))
            elif i < 256:
                data.append((False, '192.168.0.0/255.%d.0.0' % i, '192.168.0.0/255.%d.0.0' % i))
            else:
                data.append((False, '192.168.0.0/255.%d.0.0' % i, '192.168.0.0/255.%d.0.0' % i))

            if i < 64:
                data.append((False, '192.168.0.0/%d.0.0.0' % i, '0.0.0.0/%d.0.0.0' % i))
            elif i < 128:
                data.append((False, '192.168.0.0/%d.0.0.0' % i, '64.0.0.0/%d.0.0.0' % i))
            elif i < 192:
                data.append((False, '192.168.0.0/%d.0.0.0' % i, '128.0.0.0/%d.0.0.0' % i))
            else:
                data.append((False, '192.168.0.0/%d.0.0.0' % i, '192.0.0.0/%d.0.0.0' % i))

        error_str = self._run_normalize_address(data)
        self.assertEquals(error_str, "", error_str)


    def test_normalize_address_ipv6_short_notation(self):
        '''Test normalize_address() with ipv6_short_notation'''
        data = [
                 (True, 'fe80:0000:0000:0000:0211:aaaa:bbbb:d54c', 'fe80::211:aaaa:bbbb:d54c'),
                 (True, '2001:0db8:85a3:08d3:1319:8a2e:0370:734', '2001:db8:85a3:8d3:1319:8a2e:370:734'),
                ]
        error_str = self._run_normalize_address(data)
        self.assertEquals(error_str, "", error_str)

    def test_normalize_address_invalid_netmask(self):
        '''Test normalize_address() with invalid_netmask'''
        data = [
                 (True, '::1/-1', ValueError),
                 (True, '::1/129', ValueError),
                 (True, '::1/3e', ValueError),
                 (False, '192.168.0.1/-1', socket.error),
                 (False, '192.168.0.1/33', ValueError),
                 (False, '192.168.0.1/e1', socket.error),
                ]
        for (v6, ip, expected) in data:
            print("%s v6=%s" % (ip, v6))
            tests.unit.support.check_for_exception(self, expected, ufw.util.normalize_address, ip, v6)

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
        '''Test human_sort()'''
        s = '80,a222,a32,a2,b1,443,telnet,3,ZZZ,http'
        expected = '3,80,443,a2,a32,a222,b1,http,telnet,ZZZ'

        tmp = s.split(',')
        ufw.util.human_sort(tmp)
        res = ",".join(tmp)
        self.assertEquals(str(res), expected)

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
