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
import ufw.backend_iptables
import ufw.common
import ufw.frontend
import os
import re
import time

class BackendIptablesTestCase(unittest.TestCase):
    def setUp(self):
        ufw.common.do_checks = False

        # don't duplicate all the code for set_rule() from frontend.py so
        # the frontend's set_rule() to exercise our set_rule()
        self.ui = ufw.frontend.UFWFrontend(dryrun=True)

        # for convenience
        self.backend = self.ui.backend

        self.prevpath = os.environ['PATH']
        os.environ['PATH'] = "%s:%s" % (ufw.common.iptables_dir,
                                        os.environ['PATH'])

        # update ufw-init-functions to use our fake iptables* commands
        f = os.path.join(ufw.common.state_dir, "ufw-init-functions")
        contents = ""
        for line in open(f).readlines():
            if re.search("^PATH=", line):
                line = "#" + line
                line += 'PATH="%s:%s"\n' % (ufw.common.iptables_dir,
                                            line.split('"')[1])
            contents += line
        open(f + '.new', 'w').write(contents)
        os.rename(f + '.new', f)

    def tearDown(self):
        self.backend = None
        os.environ['PATH'] = self.prevpath

    def test_get_default_application_policy(self):
        '''Test get_default_application_policy()'''
        s = self.backend.get_default_application_policy()
        self.assertTrue(s.endswith("skip"))

    def test_set_default_policy(self):
        '''Test set_default_policy()'''
        # dryrun
        for direction in ['incoming', 'outgoing']:
            for policy in ['allow', 'deny', 'reject']:
                res = self.backend.set_default_policy(policy, direction)
                self.assertTrue(policy in res,
                                "Could not find '%s' in:\n%s" % (policy, res))
                self.assertTrue(direction in res,
                                "Could not find '%s' in:\n%s" % (direction,
                                                                 res))

        # no dryrun
        self.backend.dryrun = False
        for direction in ['incoming', 'outgoing']:
            for policy in ['allow', 'deny', 'reject']:
                res = self.backend.set_default_policy(policy, direction)
                self.assertTrue(policy in res,
                                "Could not find '%s' in:\n%s" % (policy, res))
                self.assertTrue(direction in res,
                                "Could not find '%s' in:\n%s" % (direction,
                                                                 res))
                if direction == 'incoming':
                    res = self.backend._get_default_policy("input")
                else:
                    res = self.backend._get_default_policy("output")
                self.assertEquals(res, policy)

    def test_get_running_raw(self):
        '''Test get_running_raw()'''
        # dryrun
        for t in ['raw', 'builtins', 'before', 'user', 'after', 'logging']:
            res = self.backend.get_running_raw(t)
            for s in ['iptables', 'ip6tables']:
                self.assertTrue("Checking raw %s" % s in res, 
                                "Could not find '%s' in:\n%s" % (s, res))

        # no dryrun
        self.backend.dryrun = False
        for t in ['raw', 'builtins', 'before', 'user', 'after', 'logging']:
            res = self.backend.get_running_raw(t)
            self.assertTrue(t in res, "Could not find '%s' in:\n%s" % \
                            (t, res))

    def test_get_status(self):
        '''Test get_status()'''
        # build up some rules
        cmds_sim = tests.unit.support.get_sample_rule_commands_simple()
        cmds_ext = tests.unit.support.get_sample_rule_commands_extended()

        for cmds in [cmds_sim, cmds_ext]:
            self.backend.rules = []
            self.backend.rules6 = []
            for cmd in cmds:
                pr = ufw.frontend.parse_command(cmd + [])
                action = cmd[1]
                self.assertEquals(action, pr.action, "%s != %s" % (action, \
                                                               pr.action))
                if 'rule' in pr.data:
                    if pr.data['rule'].v6:
                        self.backend.rules6.append(pr.data['rule'])
                    else:
                        self.backend.rules.append(pr.data['rule'])

            # dryrun
            self.backend.dryrun = True
            for v in [False, True]:
                for c in [False, True]:
                    res = self.backend.get_status(verbose=v, show_count=c)
                    for s in ['iptables', 'ip6tables']:
                        self.assertTrue("Checking %s" % s in res, 
                                        "Could not find '%s' in:\n%s" % (s, res))

            # no dryrun
            self.backend.dryrun = False
            for v in [False, True]:
                for c in [False, True]:
                    res = self.backend.get_status(verbose=v, show_count=c)
                    terms = ['Status: active', 'To']
                    if v:
                        terms += ['Logging: on', 'Default: deny', 
                                  'New profiles: skip']
                    if c:
                        terms += '[ 1] '
                    for search in terms:
                        self.assertTrue(search in res, 
                                        "Could not find '%s' in:\n%s" % (search,
                                                                     res))


    def test_stop_firewall(self):
        '''Test stop_firewall()'''
        self.backend.stop_firewall()
        self.backend.dryrun = False
        self.backend.stop_firewall()
        # TODO: verify output

    def test_start_firewall(self):
        '''Test start_firewall()'''
        self.backend.start_firewall()
        self.backend.dryrun = False
        self.backend.start_firewall()
        # TODO: verify output

    def test__need_reload(self):
        '''Test _need_reload()'''
        for v6 in [False, True]:
            res = self.backend._need_reload(v6)
            self.backend.dryrun = False
            res = self.backend._need_reload(v6)
            self.assertFalse(res)
            # TODO: verify output

    def test__reload_user_rules(self):
        '''Test _reload_user_rules()'''
        self.backend.defaults['enabled'] = "no"
        self.backend._reload_user_rules()
        self.backend.dryrun = False
        self.backend.defaults['enabled'] = "yes"
        self.backend._reload_user_rules()
        # TODO: verify output

    def test__get_rules_from_formatted(self):
        '''TODO: '''
        pass

    def test__get_lists_from_formatted(self):
        '''TODO: '''
        pass

    def test__read_rules(self):
        '''TODO: '''
        pass

    def test__write_rules(self):
        '''TODO: '''
        pass

    def test_set_rule(self):
        '''Test set_rule()'''
        self.ui.backend.dryrun = False # keeps the verbosity down
        # TODO: optimize this. We don't need to hit the disk for all of these.
        #       maybe set enabled to 'yes' once for each branch
        self.ui.backend.defaults['enabled'] = "yes"
        cmds_sim = tests.unit.support.get_sample_rule_commands_simple()
        for cmd in cmds_sim:
            pr = ufw.frontend.parse_command(cmd + [])
            action = cmd[1]
            self.assertEquals(action, pr.action, "%s != %s" % (action, \
                                                               pr.action))
            if 'rule' in pr.data:
                self.ui.do_action(pr.action, pr.data['rule'], \
                                  pr.data['iptype'], True)
            # TODO: verify output

    def test_get_app_rules_from_system(self):
        '''TODO: '''
        pass

    def test__chain_cmd(self):
        '''TODO: '''
        pass

    def test_update_logging(self):
        '''Test update_logging()'''
        self.backend.dryrun = True
        self.backend.defaults['enabled'] = "no"
        self.backend.dryrun = False
        for level in ['off', 'low', 'medium', 'high', 'full']:
            self.backend.defaults['enabled'] = "no"
            self.backend.update_logging(level)
            self.backend.defaults['enabled'] = "yes"
            self.backend.update_logging(level)
            # TODO: verify output

    def test__get_logging_rules(self):
        '''TODO: '''
        pass

    def test_reset(self):
        '''Test reset()'''
        res = self.backend.reset()
        print (res)

        # we only have 1 second resolution on the backup, so sleep is needed
        time.sleep(1)

        self.backend.dryrun = False
        res = self.backend.reset()
        print (res)
        # TODO: verify output


def test_main(): # used by runner.py
    tests.unit.support.run_unittest(
            BackendIptablesTestCase
    )

if __name__ == "__main__": # used when standalone
    unittest.main()
