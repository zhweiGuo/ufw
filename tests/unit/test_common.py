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
import ufw.common

class CommonTestCase(unittest.TestCase):
    def setUp(self):
        self.rules = {
                "any":  ufw.common.UFWRule("allow", "any"),
                "ipv6": ufw.common.UFWRule("deny", "ipv6"),
                "tcp":  ufw.common.UFWRule("limit", "tcp"),
                "udp":  ufw.common.UFWRule("reject", "udp"),
                "full-any":  ufw.common.UFWRule("allow", "any",
                    dport="123", dst="10.0.0.1", sport="124",
                    src="10.0.0.2", direction="in"),
                "full-ipv6": ufw.common.UFWRule("deny", "ipv6",
                    dport="123", dst="10.0.0.1", sport="124",
                    src="10.0.0.2", direction="in"),
                "full-tcp":  ufw.common.UFWRule("limit", "tcp",
                    dport="123", dst="10.0.0.1", sport="124",
                    src="10.0.0.2", direction="out"),
                "full-udp":  ufw.common.UFWRule("reject", "udp",
                    dport="123", dst="10.0.0.1", sport="124",
                    src="10.0.0.2", direction="out"),
                "dapp":  ufw.common.UFWRule("allow", "any"),
                "sapp":  ufw.common.UFWRule("deny", "any"),
                }
        self.rules['dapp'].dapp = "Apache"
        self.rules['dapp'].dport = "80"
        self.rules['dapp'].proto = "tcp"
        self.rules['sapp'].sapp = "Apache"
        self.rules['sapp'].sport = "80"
        self.rules['sapp'].proto = "tcp"

    def tearDown(self):
        self.rules = None

    def test_ufwerror(self):
        '''Test UFWError'''
        try:
            raise ufw.common.UFWError("test")
        except ufw.common.UFWError as e:
            self.assertEquals(e.value, "test", "'%s' != 'test'" % e.value)
            return
        self.assertTrue(False, "Did not raise an error")

    def test__get_attrib(self):
        '''Test _get_attrib()'''
        self.rules["any"]._get_attrib()

    def test_dup_rule(self):
        '''Test dup_rule()'''
        r = self.rules["any"].dup_rule()
        self.assertEquals(ufw.common.UFWRule.match(r, self.rules["any"]), 0)

    def test_format_rule(self):
        '''Test format_rule()'''
        s = str(self.rules["any"])
        self.assertEquals(s, "-p all -j ACCEPT")

    def test_set_action(self):
        '''Test set_action()'''
        r = self.rules["any"]
        for action in ['allow', 'deny', 'reject', 'limit']:
            r.set_action(action)
            self.assertEquals(action, r.action, "%s != %s" %
                              (action, r.action))

    def test_set_port(self):
        '''Test set_port()'''
        rule = self.rules["any"]
        for loc in ['dst', 'src']:
            for port in ['any',
                         '1',
                         '22',
                         '1023',
                         '1024',
                         '1025',
                         '65535',
                         '1,2,3,4,5,6,7,8,9,10,11,12,13,14,15',
                         '80,443,8080:8090',
                         '22:25']:
                r = rule.dup_rule()
                r.set_port(port, loc)
                if loc == 'dst':
                    self.assertEquals(port, r.dport, "%s != %s" % (port,
                                                                   r.dport))
                else:
                    self.assertEquals(port, r.sport, "%s != %s" % (port,
                                                                   r.sport))

        r = self.rules["dapp"].dup_rule()
        r.dapp = "Apache"
        r.set_port("Apache", "dst")
        self.assertEquals(r.dapp, r.dport, "%s != %s" % (r.dapp, r.dport))
            
        r = self.rules["sapp"].dup_rule()
        r.sapp = "Apache"
        r.set_port("Apache", "src")
        self.assertEquals(r.sapp, r.sport, "%s != %s" % (r.sapp, r.sport))

    def test_set_port_bad(self):
        '''Test set_port() - bad'''
        rule = self.rules["any"]
        for loc in ['dst', 'src']:
            for port in ['an',
                         '0',
                         ',',
                         '',
                         ' ',
                         22,
                         '65536',
                         ',443,8080:8090',
                         '443:8080:8090',
                         '0:65536',
                         '2:1',
                         '80,',
                         '80,443,8080:',
                         ':8090',
                         '1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16',
                        ]:
                r = rule.dup_rule()
                e = ufw.common.UFWError
                if port == 22:
                    e = TypeError
                tests.unit.support.check_for_exception(self, 
                                                       e,
                                                       r.set_port,
                                                       port,
                                                       loc)

    def test_set_protocol(self):
        '''Test set_protocol()'''
        r = self.rules["any"]
        for proto in ['any', 'tcp', 'udp', 'ipv6', 'esp', 'ah']:
            r.set_protocol(proto)
            self.assertEquals(proto, r.protocol, "%s != %s" %
                              (proto, r.protocol))

    def test_set_protocol_bad(self):
        '''Test set_protocol() - bad'''
        r = self.rules["any"]
        for proto in ['an', 'cp', 'up', 'nonexistent']:
            tests.unit.support.check_for_exception(self, 
                                                   ufw.common.UFWError,
                                                   r.set_protocol,
                                                   proto)

    def _test__fix_anywhere(self):
        '''TODO: Test _fix_anywhere()'''

    def test_set_v6(self):
        '''Test set_v6()'''
        r = self.rules["any"]
        for ipv6 in [True, False]:
            r.set_v6(ipv6)
            self.assertEquals(ipv6, r.v6, "%s != %s" %
                              (ipv6, r.v6))

    def test_set_src(self):
        '''Test set_src()'''
        r = self.rules["any"]
        for src in ["10.0.0.3"]:
            r.set_src(src)
            self.assertEquals(src, r.src, "%s != %s" %
                              (src, r.src))

    def test_set_src_bad(self):
        '''Test set_src() - bad'''
        r = self.rules["any"]
        for src in ["10.0.0.", "10..0.0.3"]:
            tests.unit.support.check_for_exception(self, 
                                                   ufw.common.UFWError,
                                                   r.set_src,
                                                   src)

    def test_set_dst(self):
        '''Test set_dst()'''
        r = self.rules["any"]
        for dst in ["10.0.0.3"]:
            r.set_dst(dst)
            self.assertEquals(dst, r.dst, "%s != %s" %
                              (dst, r.dst))

    def test_set_dst_bad(self):
        '''Test set_dst() - bad'''
        r = self.rules["any"]
        for dst in ["10.0.0.", "10..0.0.3"]:
            tests.unit.support.check_for_exception(self, 
                                                   ufw.common.UFWError,
                                                   r.set_dst,
                                                   dst)

    def test_set_interface(self):
        '''Test set_interface()'''
        r = self.rules["any"]
        for if_type in ["in", "out"]:
            for interface in ["eth0", "wlan1"]:
                r.set_interface(if_type, interface)
                if if_type == "in":
                    self.assertEquals(interface, r.interface_in, "%s != %s" %
                                      (interface, r.interface_in))
                else:
                    self.assertEquals(interface, r.interface_out, "%s != %s" %
                                      (interface, r.interface_out))

    def test_set_interface_bad(self):
        '''Test set_interface() - bad'''
        r = self.rules["any"]
        interface = "eth0"
        for if_type in ["ina", "ot"]:
            tests.unit.support.check_for_exception(self, 
                                                   ufw.common.UFWError,
                                                   r.set_interface,
                                                   if_type,
                                                   interface)

        for if_type in ["in", "out"]:
            for interface in ["\tfoo", "<$%", "0eth", "eth0:0"]:
                tests.unit.support.check_for_exception(self, 
                                                       ufw.common.UFWError,
                                                       r.set_interface,
                                                       if_type,
                                                       interface)

    def test_set_position(self):
        '''Test set_position()'''
        r = self.rules["any"]
        r.set_position(2)
        self.assertEquals(2, r.position)

    def test_set_position_bad(self):
        '''Test set_position() - bad'''
        r = self.rules["any"]
        tests.unit.support.check_for_exception(self, 
                                               ufw.common.UFWError,
                                               r.set_position,
                                               'a')

    def test_set_logtype(self):
        '''Test set_logtype()'''
        r = self.rules["any"]
        for logtype in ["", "log", "log-all"]:
            r.set_logtype(logtype)
            self.assertEquals(logtype, r.logtype, "%s != %s" %
                              (logtype, r.logtype))

    def test_set_logtype_bad(self):
        '''Test set_logtype() - bad'''
        r = self.rules["any"]
        for logtype in ["a", "loga", "d"]:
            tests.unit.support.check_for_exception(self, 
                                                   ufw.common.UFWError,
                                                   r.set_logtype,
                                                   logtype)

    def test_set_direction(self):
        '''Test set_direction()'''
        r = self.rules["any"]
        for direction in ["in", "out"]:
            r.set_direction(direction)
            self.assertEquals(direction, r.direction, "%s != %s" %
                              (direction, r.direction))

    def test_set_direction_bad(self):
        '''Test set_direction() - bad'''
        r = self.rules["any"]
        for direction in ["", "ina", "outta"]:
            tests.unit.support.check_for_exception(self, 
                                                   ufw.common.UFWError,
                                                   r.set_direction,
                                                   direction)

    def test_normalize(self):
        '''Test normalize()'''
        for rule in self.rules.keys():
            r = self.rules[rule].dup_rule()
            r.normalize()

    def test_match(self):
        '''Test match()'''
        x = self.rules["full-any"].dup_rule()
        y = self.rules["full-any"].dup_rule()
        self.assertEquals(ufw.common.UFWRule.match(x, y), 0)

        for action in ['reject', 'deny', 'limit']:
            y = self.rules["full-any"].dup_rule()
            y.set_action(action)
            self.assertEquals(ufw.common.UFWRule.match(x, y), -1)

        for logtype in ['log', 'log-all']:
            y = self.rules["full-any"].dup_rule()
            y.set_logtype(logtype)
            self.assertEquals(ufw.common.UFWRule.match(x, y), -1)

        y = self.rules["full-any"].dup_rule()
        y.set_port("456", loc="dst")
        self.assertEquals(ufw.common.UFWRule.match(x, y), 1)

        y = self.rules["full-any"].dup_rule()
        y.set_port("456", loc="src")
        self.assertEquals(ufw.common.UFWRule.match(x, y), 1)

        y = self.rules["full-any"].dup_rule()
        y.set_protocol("tcp")
        self.assertEquals(ufw.common.UFWRule.match(x, y), 1)

        y = self.rules["full-any"].dup_rule()
        y.set_src("192.168.0.1")
        self.assertEquals(ufw.common.UFWRule.match(x, y), 1)

        y = self.rules["full-any"].dup_rule()
        y.set_dst("192.168.0.1")
        self.assertEquals(ufw.common.UFWRule.match(x, y), 1)

        y = self.rules["full-any"].dup_rule()
        y.set_dst("fe80::1")
        self.assertEquals(ufw.common.UFWRule.match(x, y), 1)

        y = ufw.common.UFWRule("allow", "tcp", dst="fe80::1")
        self.assertEquals(ufw.common.UFWRule.match(x, y), 1)

        y = self.rules["full-any"].dup_rule()
        y.sapp = "OpenSSH"
        self.assertEquals(ufw.common.UFWRule.match(x, y), 1)

        y = self.rules["full-any"].dup_rule()
        y.dapp = "OpenSSH"
        self.assertEquals(ufw.common.UFWRule.match(x, y), 1)

        y = self.rules["full-any"].dup_rule()
        y.set_interface("in", "eth0")
        self.assertEquals(ufw.common.UFWRule.match(x, y), 1)

        x = ufw.common.UFWRule("allow", "tcp", direction="out")
        y = x.dup_rule()
        y.set_interface("out", "eth0")
        self.assertEquals(ufw.common.UFWRule.match(x, y), 1)

        x = ufw.common.UFWRule("allow", "tcp", direction="out")
        x.set_interface("out", "eth0")
        y = x.dup_rule()
        y.set_interface("in", "eth0")
        self.assertEquals(ufw.common.UFWRule.match(x, y), 1)

    def test_fuzzy_dst_match(self):
        '''Test fuzzy_dst_match()'''
        x = self.rules["full-any"].dup_rule()
        y = self.rules["full-any"].dup_rule()
        self.assertEquals(ufw.common.UFWRule.fuzzy_dst_match(x, y), 0)
        x.set_protocol("tcp")
        self.assertEquals(ufw.common.UFWRule.fuzzy_dst_match(x, y), -1)
        self.assertEquals(ufw.common.UFWRule.fuzzy_dst_match(y, x), 1)

    def test__is_anywhere(self):
        '''Test _is_anywhere()'''
        r = self.rules['any']
        self.assertTrue(r._is_anywhere("::/0"))
        self.assertTrue(r._is_anywhere("0.0.0.0/0"))
        self.assertFalse(r._is_anywhere("::1"))
        self.assertFalse(r._is_anywhere("fe80::1/16"))
        self.assertFalse(r._is_anywhere("127.0.0.1"))
        self.assertFalse(r._is_anywhere("127.0.0.1/32"))

    def test_get_app_tuple(self):
        '''Test get_app_tuple()'''
        r = self.rules['dapp'].dup_rule()
        t = r.get_app_tuple().split()
        self.assertEquals(self.rules['dapp'].dapp, t[0])
        self.assertEquals(self.rules['dapp'].dst, t[1])
        self.assertEquals("any", t[2])
        self.assertEquals("0.0.0.0/0", t[3])
        r.set_interface("in", "eth0")
        t = r.get_app_tuple().split()
        self.assertEquals(self.rules['dapp'].dapp, t[0])
        self.assertEquals(self.rules['dapp'].dst, t[1])
        self.assertEquals("any", t[2])
        self.assertEquals("0.0.0.0/0", t[3])
        self.assertEquals("in_eth0", t[4])

        r = self.rules['sapp'].dup_rule()
        t = r.get_app_tuple().split()
        self.assertEquals("any", t[0])
        self.assertEquals("0.0.0.0/0", t[1])
        self.assertEquals(self.rules['sapp'].sapp, t[2])
        self.assertEquals(self.rules['sapp'].src, t[3])
        r.set_interface("out", "eth0")
        t = r.get_app_tuple().split()
        self.assertEquals("any", t[0])
        self.assertEquals("0.0.0.0/0", t[1])
        self.assertEquals(self.rules['sapp'].sapp, t[2])
        self.assertEquals(self.rules['sapp'].src, t[3])
        self.assertEquals("out_eth0", t[4])


def test_main(): # used by runner.py
    tests.unit.support.run_unittest(
            CommonTestCase
    )

if __name__ == "__main__": # used when standalone
    unittest.main()
