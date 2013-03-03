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
import os
import tests.unit.support
import ufw.common
import ufw.frontend

class FrontendTestCase(unittest.TestCase):
    def setUp(self):
        ufw.common.do_checks = False
        ufw.common.state_dir = os.path.join(
                                os.path.realpath(tests.unit.support.topdir),
                                "ufw/lib/ufw")
        ufw.common.share_dir = os.path.join(
                                os.path.realpath(tests.unit.support.topdir),
                                "ufw/usr/share/ufw")
        ufw.common.trans_dir = ufw.common.share_dir
        ufw.common.config_dir = os.path.join(
                                 os.path.realpath(tests.unit.support.topdir),
                                 "ufw/etc")
        ufw.common.prefix_dir = os.path.join(
                                os.path.realpath(tests.unit.support.topdir),
                                "ufw/usr")
        iptables_dir = ""
        for d in ["/sbin", "/bin",
                  "/usr/sbin", "/usr/bin",
                  "/usr/local/sbin", "/usr/local/bin"]:
            if os.path.exists(os.path.join(d, "iptables")):
                iptables_dir = d
                break
        self.assertTrue(iptables_dir != "")
        ufw.common.iptables_dir = iptables_dir

        self.ui = ufw.frontend.UFWFrontend(dryrun=True)

    def tearDown(self):
        self.ui = None

    def test_parse_command(self):
        '''Test parse_command()'''
        # test_parser.py will handle command combinations exhaustively, let's
        # just use a representative set here
        cmds = [
                'enable',
                'disable',
                'reload',
                'default allow',
                'default deny',
                'default reject',
                'default allow incoming',
                'default deny outgoing',
                'logging on',
                'logging off',
                'logging medium',
                'reset',
                'status',
                'status numbered',
                'status verbose',
                'show raw',
                'show builtins',
                'show before-rules',
                'show user-rules',
                'show after-rules',
                'show logging-rules',
                'show listening',
                'show added',
                'delete 1',
                'delete reject 22',
                'insert 1 limit 22/tcp',
                'allow 53/udp',
                'deny http',
                'allow to any port 23 proto tcp',
                'deny from 192.168.0.1 to 192.168.0.2',
                'reject in on eth0',
                'allow to fe80::/16',
                'deny from any port 53 proto udp',
                'limit in on eth0 to 192.168.0.1 port 22 from 10.0.0.0/24 port 1024:65535 proto tcp',
                '--version',
                '--dry-run allow 22/tcp',
                '--dry-run app list',
                'app list',
                'app info Apache',
                'app default skip',
                'app update Apache',
               ]
        for c in cmds:
            #print(c)
            ufw.frontend.parse_command(['ufw'] + c.split())
        
    def test_get_command_help(self):
        '''Test get_command_help()'''
        s = ufw.frontend.get_command_help()
        terms = ['enable',
                 'disable',
                 'default ARG',
                 'logging LEVEL',
                 'allow ARGS',
                 'deny ARGS',
                 'reject ARGS',
                 'limit ARGS',
                 'delete RULE|NUM',
                 'insert NUM RULE',
                 'reload',
                 'reset',
                 'status',
                 'status numbered',
                 'status verbose',
                 'show ARG',
                 'version',
                 'app list',
                 'app info PROFILE',
                 'app update PROFILE',
                 'app default ARG'
                ]
        for search in terms:
            self.assertTrue(search in s, "Could not find '%s' in:\n%s" % \
                            (search, s))
        
    def test_continue_under_ssh(self):
        '''Test continue_under_ssh()'''
        self.ui.continue_under_ssh()

    def test_do_action(self):
        '''Test do_action()'''
        cmds = [
                'enable',
                'disable',
                'enable',
                'reload',
                'default allow',
                'default deny',
                'default reject',
                'default allow incoming',
                'default deny outgoing',
                'logging on',
                'logging off',
                'logging medium',
                'reset',
                'status',
                'status numbered',
                'status verbose',
                'allow 43',
                'reject 22',
                'delete 1',
                'delete reject 22',
                'insert 1 limit 22/tcp',
                'allow 53/udp',
                'deny http',
                'allow to any port 23 proto tcp',
                'deny from 192.168.0.1 to 192.168.0.2',
                'reject in on eth0',
                'allow to fe80::/16',
                'deny from any port 53 proto udp',
                'limit in on eth0 to 192.168.0.1 port 22 from 10.0.0.0/24 port 1024:65535 proto tcp',
               ]
        for c in cmds:
            try:
                pr = ufw.frontend.parse_command(['ufw'] + c.split())
                if 'rule' in pr.data:
                    res = self.ui.do_action(pr.action,
                                            pr.data['rule'],
                                            pr.data['iptype'],
                                            force=True)
                else:
                    res = self.ui.do_action(pr.action, "", "", force=True)
            except Exception:
                print("%s failed:" % c)
                raise
            self.assertTrue(res != "", "Output is empty for '%s'" % c)
        print ("TODO: verify output of do_action()")

    def test_do_application_action(self):
        '''Test do_application_action()'''
        cmds = [
                'app list',
                'app info WWW',
                'app default skip',
                'app update WWW',
               ]
        for c in cmds:
            try:
                pr = ufw.frontend.parse_command(['ufw'] + c.split())
                if 'type' in pr.data and pr.data['type'] == 'app':
                    res = self.ui.do_application_action(pr.action,
                                                        pr.data['name'])
                else:
                    res = self.ui.do_action(pr.action, "", "", force=True)
            except Exception:
                print("%s failed:" % c)
                raise
            if c.startswith("app update"):
                self.assertTrue(res == "", "Output is not empty for '%s'" % c)
            else:
                self.assertTrue(res != "", "Output is empty for '%s'" % c)
        print ("TODO: verify output of do_application_action()")

def test_main(): # used by runner.py
    tests.unit.support.run_unittest(
            FrontendTestCase
    )

if __name__ == "__main__": # used when standalone
    unittest.main()
