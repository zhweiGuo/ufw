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

import re
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

    def test_ufwcommand_parse(self):
        '''Test UFWCommand.parse()'''
        c = ufw.parser.UFWCommand('basic', 'status')
        pr = c.parse(['status'])
        self.assertEquals('status', pr.action, "%s != 'status'" % (pr.action))

    def test_ufwcommand_rule_get_command(self):
        '''Test UFWCommandRule.get_command()'''
        count = 0
        cmds = tests.unit.support.get_sample_rule_commands_simple()
        cmds += tests.unit.support.get_sample_rule_commands_extended()
        cmds += tests.unit.support.get_sample_rule_commands_extended(v6=True)
        cmds += [
                 ['rule', 'reject', 'from', 'any', 'app', 'Apache'],
                 ['rule', 'reject', 'from', 'any', 'port', 'smtp'],
                ]
        errors = []
        pat_in = re.compile(r' in ')
        for cmd in cmds:
            count += 1
            #print(" ".join(cmd))
            # Note, parser.parse_command() modifies it arg, so pass a copy of
            # the cmd, not a reference
            pr = self.parser.parse_command(cmd + [])
            res = ufw.parser.UFWCommandRule.get_command(pr.data['rule'])
            cmd_compare = cmd + []

            # Massage the cmd_compare output to what we expect

            # remove 'in' on rules with an interface
            if 'in' in cmd_compare and 'on' not in cmd_compare:
                cmd_compare.remove('in')

            # use '1/tcp' instead of 'tcpmux' for simple rules and
            # 'port 1 proto tcp' for extended
            if 'tcpmux' in cmd_compare:
                if 'to' in cmd_compare or 'from' in cmd_compare:  # extended
                    cmd_compare[cmd_compare.index('tcpmux')] = '1'
                    if 'proto' not in cmd_compare:
                        cmd_compare.append('proto')
                        cmd_compare.append('tcp')
                    if 'tcpmux' in cmd_compare:  # can have 2 in extended rules
                        cmd_compare[cmd_compare.index('tcpmux')] = '1'
                else:  # simple
                    cmd_compare[cmd_compare.index('tcpmux')] = '1/tcp'

            # use '21/udp' instead of 'fsp' for simple rules and
            # 'port 21 proto udp' for extended
            if 'fsp' in cmd_compare:
                if 'to' in cmd_compare or 'from' in cmd_compare:  # extended
                    cmd_compare[cmd_compare.index('fsp')] = '21'
                    if 'proto' not in cmd_compare:
                        cmd_compare.append('proto')
                        cmd_compare.append('udp')
                    if 'fsp' in cmd_compare:  # can have 2 in extended rules
                        cmd_compare[cmd_compare.index('fsp')] = '21'
                else:  # simple rule
                    cmd_compare[cmd_compare.index('fsp')] = '21/udp'

            # use 'port 25 proto tcp' in extended rules
            if 'smtp' in cmd_compare and 'proto' not in cmd_compare:
                cmd_compare[cmd_compare.index('smtp')] = '25'
                cmd_compare.append('proto')
                cmd_compare.append('tcp')

            # remove 'from any' clause when used without port or app
            if 'from' in cmd_compare and \
               cmd_compare[cmd_compare.index('from') + 1] == 'any' and \
               (len(cmd_compare) - 2 == cmd_compare.index('from') or \
                (cmd_compare.index('from') + 2 < len(cmd_compare) and \
                 cmd_compare[cmd_compare.index('from') + 2] != 'port' and \
                 cmd_compare[cmd_compare.index('from') + 2] != 'app')):
                del cmd_compare[cmd_compare.index('from') + 1]
                cmd_compare.remove('from')

            # remove 'to any' clause when used without port or app when 'from'
            # or 'proto' is present ('from' will not be 'any' because of above)
            if ('from' in cmd_compare or 'proto' in cmd_compare or \
                'on' in cmd_compare) and 'to' in cmd_compare and \
               cmd_compare[cmd_compare.index('to') + 1] == 'any' and \
               (len(cmd_compare) - 2 == cmd_compare.index('to') or \
                (cmd_compare.index('to') + 2 < len(cmd_compare) and \
                 cmd_compare[cmd_compare.index('to') + 2] != 'port' and \
                 cmd_compare[cmd_compare.index('to') + 2] != 'app')):
                del cmd_compare[cmd_compare.index('to') + 1]
                cmd_compare.remove('to')

            # remove 'to any' if no 'from' clause (ie, convert extended to
            # simple)
            if 'to' in cmd_compare and 'from' not in cmd_compare and \
               cmd_compare[cmd_compare.index('to') + 1] == 'any' and \
               cmd_compare.index('to') + 2 < len(cmd_compare) and \
               'on' not in cmd_compare:
                if 'port' in cmd_compare:
                    port = "%s" % cmd_compare[cmd_compare.index('port') + 1]
                    if 'proto' in cmd_compare:
                        port += "/%s" % \
                                cmd_compare[cmd_compare.index('proto') + 1]
                    del cmd_compare[cmd_compare.index('proto') + 1]
                    cmd_compare.remove('proto')
                    del cmd_compare[cmd_compare.index('port') + 1]
                    cmd_compare.remove('port')
                    del cmd_compare[cmd_compare.index('to') + 1]
                    cmd_compare.remove('to')
                    cmd_compare.append(port)
                elif 'app' in cmd_compare:
                    del cmd_compare[cmd_compare.index('to') + 2]
                    del cmd_compare[cmd_compare.index('to') + 1]
                    cmd_compare.remove('to')

            if "rule %s" % res != " ".join(cmd_compare):
                errors.append(" 'rule %s' != '%s' (orig=%s)" % (res,
                                                      " ".join(cmd_compare),
                                                      cmd))
        self.assertEquals(len(errors), 0,
                          "Rules did not match:\n%s\n(%d of %d)" % \
                          ("\n".join(errors), len(errors), count))

    def test_simple_parse(self):
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

    def test_misc_rules_parse(self):
        '''Test rule syntax - miscellaneous'''
        cmds = [
                ['rule', 'delete', '1'],
                ['rule', 'delete', 'allow', '22'],
                ['rule', 'deny', 'from', 'any', 'port', 'domain', 'to', \
                 'any', 'port', 'tftp'],
                ['rule', 'deny', 'to', 'any', 'proto', 'ipv6'],
                ['rule', 'deny', 'to', 'any', 'proto', 'esp'],
                ['rule', 'deny', 'to', 'any', 'proto', 'ah'],
               ]
        count = 0
        for cmd in cmds:
            #print(" ".join(cmd))
            count += 1
            # Note, parser.parse_command() modifies it arg, so pass a copy of
            # the cmd, not a reference
            self.parser.parse_command(cmd + [])

    def test_rule_bad_syntax(self):
        '''Test rule syntax - bad'''
        cmds = [
                (['rule', 'insert', '1', 'allow'], ValueError),
                (['rule', 'insert', 'a', 'allow', '22'], ufw.common.UFWError),
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
                (['rule', 'reject', 'in', 'on', 'eth0', 'port', '22'],
                 ufw.common.UFWError),
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
                (['rule', 'badcmd', 'to', 'any'], ValueError),
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
                (['rule', 'allow', 'from', 'any', 'port', 'tftp', 'to', 'any',
                 'port', 'smtp'], ufw.common.UFWError),
                (['rule', 'deny', 'from', 'any', 'port', 'smtp', 'to', 'any',
                 'port', 'tftp', 'proto', 'any'], ufw.common.UFWError),
                (['rule', 'allow', 'nope', 'any', 'to', 'any'],
                 ufw.common.UFWError),
                (['rule', 'deny', 'to', 'any', 'port', 'tftp', \
                  'proto', 'tcp'], ufw.common.UFWError),
                (['rule', 'deny', 'to', '::1', 'proto', 'ipv6'],
                 ufw.common.UFWError),
                (['rule', 'deny', 'to', 'any', 'port', '22', 'proto', 'ipv6'],
                 ufw.common.UFWError),
                (['rule', 'deny', 'to', 'any', 'port', '22', 'proto', 'esp'],
                 ufw.common.UFWError),
                (['rule', 'deny', 'to', 'any', 'port', '22', 'proto', 'ah'],
                 ufw.common.UFWError),
               ]
        count = 0
        for cmd, exception in cmds:
            #print(" ".join(cmd))
            count += 1
            # Note, parser.parse_command() modifies it arg, so pass a copy of
            # the cmd, not a reference
            tests.unit.support.check_for_exception(self, exception,
                                                   self.parser.parse_command,
                                                   cmd + [])

    def test_extended_parse(self):
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
