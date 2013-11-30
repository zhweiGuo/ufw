#
# Copyright 2013 Canonical Ltd.
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
import ufw.parser

class ParserTestCase(unittest.TestCase):
    def setUp(self):
        self.parser = ufw.parser.UFWParser()

        # Basic commands
        for i in ['enable', 'disable', 'help', '--help', 'version', \
                  '--version', 'reload', 'reset' ]:
            self.parser.register_command(ufw.parser.UFWCommandBasic(i))

        # Application commands
        for i in ['list', 'info', 'default', 'update']:
            self.parser.register_command(ufw.parser.UFWCommandApp(i))

        # Logging commands
        for i in ['on', 'off', 'low', 'medium', 'high', 'full']:
            self.parser.register_command(ufw.parser.UFWCommandLogging(i))

        # Default commands
        for i in ['allow', 'deny', 'reject']:
            self.parser.register_command(ufw.parser.UFWCommandDefault(i))

        # Status commands ('status', 'status verbose', 'status numbered')
        for i in [None, 'verbose', 'numbered']:
            self.parser.register_command(ufw.parser.UFWCommandStatus(i))

        # Show commands
        for i in ['raw', 'before-rules', 'user-rules', 'after-rules', \
                  'logging-rules', 'builtins', 'listening', 'added']:
            self.parser.register_command(ufw.parser.UFWCommandShow(i))

        # Rule commands
        rule_commands = ['allow', 'limit', 'deny' , 'reject', 'insert', \
                         'delete']
        for i in rule_commands:
            self.parser.register_command(ufw.parser.UFWCommandRule(i))

    def tearDown(self):
        pass

    def test_ufwcommand_parse_empty(self):
        '''Test UFWCommand.parse([])'''
        c = ufw.parser.UFWCommand('basic', 'status')
        tests.unit.support.check_for_exception(self, ValueError, \
                                                   c.parse,
                                                   [])

    def test_ufwcommand_help(self):
        '''Test UFWCommand.help()'''
        c = ufw.parser.UFWCommand('basic', 'status')
        tests.unit.support.check_for_exception(self, ufw.common.UFWError, \
                                                   c.help,
                                                   [])

    def test_simple(self):
        '''Test simple rule syntax'''
        count = 0
        cmds = tests.unit.support.get_sample_rule_commands_simple()
        for cmd in cmds:
            count += 1
            #print(" ".join(cmd))
            # Note, parser.parse_command() modifies it arg, so pass a copy of
            # the cmd, not a reference
            pr = self.parser.parse_command(cmd + [])

            # TODO: more tests here by sending the cmd and the pr to a helper
            action = cmd[1]
            self.assertEquals(action, pr.action, "%s != %s" % (action, \
                                                               pr.action))

            del_cmd = cmd + []
            del_cmd.insert(1, 'delete')
            #print(" ".join(del_cmd))
            # Note, parser.parse_command() modifies it arg, so pass a copy of
            # the del_cmd, not a reference
            pr = self.parser.parse_command(del_cmd + [])

            # TODO: more tests here by sending the cmd and the pr to a helper
            action = del_cmd[2]
            self.assertEquals(action, pr.action, "%s != %s" % (action, \
                                                               pr.action))
            ins_cmd = cmd + []
            ins_cmd.insert(1, 'insert')
            ins_cmd.insert(2, '1')
            #print(" ".join(ins_cmd))
            # Note, parser.parse_command() modifies it arg, so pass a copy of
            # the del_cmd, not a reference
            pr = self.parser.parse_command(ins_cmd + [])

            # TODO: more tests here by sending the cmd and the pr to a helper
            action = ins_cmd[3]
            self.assertEquals(action, pr.action, "%s != %s" % (action, \
                                                               pr.action))
        print("%d rules checked" % count)

    def test_rule_bad_syntax(self):
        '''Test rule syntax - bad'''
        cmds = [
                (['rule', 'insert', '1', 'allow'], ValueError),
                (['rule', 'insert', '0', 'allow', '22'], ufw.common.UFWError),
                (['rule', 'allow'], ValueError),
                (['rule'], ValueError),
                (['rule', 'allow', '22', 'in', 'on', 'eth0'],
                 ufw.common.UFWError),
                (['rule', 'allow', 'in', 'in', 'eth0', '22'],
                 ufw.common.UFWError),
                (['rule', 'allow', 'in', 'on', 'eth0', '22', 'log'],
                 ufw.common.UFWError),
                (['rule', 'allow', 'in', 'on', 'eth0', '22', 'log-all'],
                 ufw.common.UFWError),
                (['rule', 'allow', 'in', 'on', 'eth0', 'log', 'to', 'any', \
                  'port', '22', 'from', 'any', 'port', '123', 'proto', 'udp', \
                  'extra'], ValueError),
                (['rule', 'allow', '22/udp/p'], ufw.common.UFWError),
                (['rule', 'allow', '22:2e'], ufw.common.UFWError),
                (['rule', 'allow', '22/ipv6'], ufw.common.UFWError),
                (['rule', 'allow', 'to', 'any', '22'], ufw.common.UFWError),
                (['rule', 'allow', 'to', 'any', 'to', '22'],
                 ufw.common.UFWError),
                (['rule', 'allow', 'to', 'any', 'proto', 'nope'],
                 ufw.common.UFWError),
                (['rule', 'allow', 'in', 'on', '!eth0', 'to', 'any'],
                 ufw.common.UFWError),
                (['rule', 'allow', 'out', 'on', 'eth0:0', 'to', 'any'],
                 ufw.common.UFWError),
                (['rule', 'allow', 'in', 'on', '$eth', 'to', 'any'],
                 ufw.common.UFWError),
                (['rule', 'allow', 'in', 'eth0', 'to', 'any'],
                 ufw.common.UFWError),
                (['rule', 'allow', 'from', 'bad_address'],
                 ufw.common.UFWError),
                (['rule', 'allow', 'to', 'bad_address'], ufw.common.UFWError),
                (['rule', 'allow', 'port', '22'], ufw.common.UFWError),
                (['rule', 'allow', 'to', 'any', 'port', '22_23'],
                 ufw.common.UFWError),
                (['rule', 'allow', 'to', 'any', 'port', '22:_23'],
                 ufw.common.UFWError),
                (['rule', 'allow', 'to', 'any', 'port', '65536'],
                 ufw.common.UFWError),
                (['rule', 'allow', 'to', '::1', 'from', '127.0.0.1'],
                 ufw.common.UFWError),
                (['rule', 'allow', 'to', 'any', 'port', 'nonexistent'],
                 ufw.common.UFWError),
                (['rule', 'allow', 'from', 'any', 'port', 'nonexistent',
                  'proto', 'any'], ufw.common.UFWError),
                (['rule', 'allow', 'from', 'any', 'port', 'tftp', 'to', 'any'
                 'port', 'smtp'], ufw.common.UFWError),
               ]
        count = 0
        for cmd, exception in cmds:
            print(" ".join(cmd))
            count += 1
            # Note, parser.parse_command() modifies it arg, so pass a copy of
            # the cmd, not a reference
            tests.unit.support.check_for_exception(self, exception,
                                                   self.parser.parse_command,
                                                   cmd + [])

    def test_extended(self):
        '''Test extended rule syntax'''
        count = 0
        cmds = tests.unit.support.get_sample_rule_commands_extended()
        cmds6 = tests.unit.support.get_sample_rule_commands_extended(v6=True)
        for cmd in cmds + cmds6:
            count += 1
            #print(" ".join(cmd))
            # Note, parser.parse_command() modifies it arg, so pass a copy of
            # the cmd, not a reference
            pr = self.parser.parse_command(cmd + [])

            # TODO: more tests here by sending the cmd and the pr to a helper
            action = cmd[1]
            self.assertEquals(action, pr.action, "%s != %s" % (action, \
                                                               pr.action))

        print("%d rules checked" % count)

    def test_simple_bad_numeric_port(self):
        '''Test simple bad numeric port'''
        for port in ['-1', '1000000']:
            c = ['rule', 'allow', port]
            tests.unit.support.check_for_exception(self, ufw.common.UFWError, \
                                                   self.parser.parse_command,
                                                   c)

    def test_bad_simple_action(self):
        '''Test bad simple action'''
        for action in ['allw', 'eny', 'nonexistent']:
            c = ['rule', action, '22']
            tests.unit.support.check_for_exception(self, ValueError, \
                                                   self.parser.parse_command,
                                                   c)

    def test_delete_bad_simple_action(self):
        '''Test delete bad simple action'''
        for action in ['allw', 'eny', 'nonexistent']:
            c = ['rule', 'delete', action, '22']
            tests.unit.support.check_for_exception(self, ValueError, \
                                                   self.parser.parse_command,
                                                   c)

    def test_bad_simple_action_with_direction(self):
        '''Test bad simple action with direction'''
        for dir in ['ina', 'ou']:
            c = ['rule', 'allow', dir, '22']
            #self.parser.parse_command(c)
            tests.unit.support.check_for_exception(self, ufw.common.UFWError, \
                                                   self.parser.parse_command,
                                                   c)

        c = ['rule', 'allow', 5, '22']
        tests.unit.support.check_for_exception(self, AttributeError, \
                                               self.parser.parse_command,
                                               c)



def test_main(): # used by runner.py
    tests.unit.support.run_unittest(
            ParserTestCase
    )

if __name__ == "__main__": # used when standalone
    unittest.main()
