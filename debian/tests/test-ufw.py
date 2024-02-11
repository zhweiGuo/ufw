#!/usr/bin/python3
#
#    test-ufw.py quality assurance test script for ufw
#    Copyright (C) 2011-2021 Canonical Ltd.
#    Author: Jamie Strandboge <jdstrand@ubuntu.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License version 3,
#    as published by the Free Software Foundation.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
import os
import shutil
import signal
import subprocess
import sys
import unittest


running_in_container = False


# http://www.chiark.greenend.org.uk/ucgi/~cjwatson/blosxom/2009-07-02-python-sigpipe.html
# This is needed so that the subprocesses that produce endless output
# actually quit when the reader goes away.
def subprocess_setup():
    # Python installs a SIGPIPE handler by default. This is usually not what
    # non-Python subprocesses expect.
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)


def cmd(command, input=None, stderr=subprocess.STDOUT, stdout=subprocess.PIPE,
        stdin=None, timeout=None, env=None):
    '''Try to execute given command (array) and return its stdout, or return
    a textual error if it failed.'''
    try:
        sp = subprocess.Popen(command, stdin=stdin, stdout=stdout,
                              stderr=stderr, close_fds=True,
                              preexec_fn=subprocess_setup, env=env,
                              universal_newlines=True)
    except OSError as e:
        return [127, str(e)]

    out, outerr = sp.communicate(input)
    # Handle redirection of stdout
    if out is None:
        out = ''
    # Handle redirection of stderr
    if outerr is None:
        outerr = ''
    return [sp.returncode, out + outerr]


class UfwCommon(unittest.TestCase):
    '''Common test cases'''
    def _setUp(self):
        '''Set up prior to each test_* function'''
        # useful for running in a VM
        for exe in ['iptables', 'ip6tables']:
            cmd([exe, '-I', 'INPUT', '-p', 'tcp',
                 '--dport', '22', '-j', 'ACCEPT'])
        global running_in_container
        if running_in_container:
            # prevent module auto-load in test environment
            shutil.copy("/etc/default/ufw", "/etc/default/ufw.autopkgtest")
            cmd(['sed', '-i', 's/^IPT_MODULES=.*/IPT_MODULES=/',
                 '/etc/default/ufw'])

    def _tearDown(self):
        '''Clean up after each test_* function'''
        self._reset()

    def _flush_firewall(self):
        '''Flush firewall'''
        if os.path.exists('/usr/lib/ufw/ufw-init'):
            cmd(['/usr/lib/ufw/ufw-init', 'flush-all'])
        else:
            # based on '/usr/lib/ufw/ufw-init flush-all'
            for exe in ['iptables', 'ip6tables']:
                cmd([exe, '-F'])
                cmd([exe, '-X'])
                cmd([exe, '-P', 'INPUT', 'ACCEPT'])
                cmd([exe, '-P', 'OUTPUT', 'ACCEPT'])
                cmd([exe, '-P', 'FORWARD', 'ACCEPT'])

                # Mangle table
                rc, report = cmd([exe, '-L', '-t', 'mangle'])
                if rc != 0:
                    continue
                for mangle_chain in ['INPUT', 'OUTPUT', 'FORWARD',
                                     'PREROUTING', 'POSTROUTING']:
                    cmd([exe, '-t', 'mangle', '-F', mangle_chain])
                    cmd([exe, '-t', 'mangle', '-P', mangle_chain,
                         'ACCEPT'])

                # Nat table
                rc, report = cmd([exe, '-L', '-t', 'nat'])
                for nat_chain in ['OUTPUT', 'PREROUTING', 'POSTROUTING']:
                    cmd([exe, '-t', 'nat', '-F', nat_chain])
                    cmd([exe, '-t', 'nat', '-P', nat_chain, 'ACCEPT'])

    def _reset(self):
        '''Flush firewall'''
        self._flush_firewall()
        cmd(['ufw', 'disable'])
        global running_in_container
        if running_in_container:
            shutil.move("/etc/default/ufw.autopkgtest", "/etc/default/ufw")
        self._update_alternatives("auto")

    def _update_alternatives(self, backend):
        '''Run update-alternatives'''
        if backend == "legacy":
            rc, report = cmd(['update-alternatives', '--set', 'iptables',
                              '/usr/sbin/iptables-legacy'])
            expected = 0
            result = 'Got exit code %d, expected %d\n' % (rc, expected)
            self.assertEqual(expected, rc, result + report)

            rc, report = cmd(['update-alternatives', '--set', 'ip6tables',
                              '/usr/sbin/ip6tables-legacy'])
            expected = 0
            result = 'Got exit code %d, expected %d\n' % (rc, expected)
            self.assertEqual(expected, rc, result + report)
        elif backend == "nft":
            rc, report = cmd(['update-alternatives', '--set', 'iptables',
                              '/usr/sbin/iptables-nft'])
            expected = 0
            result = 'Got exit code %d, expected %d\n' % (rc, expected)
            self.assertEqual(expected, rc, result + report)

            rc, report = cmd(['update-alternatives', '--set', 'ip6tables',
                              '/usr/sbin/ip6tables-nft'])
            expected = 0
            result = 'Got exit code %d, expected %d\n' % (rc, expected)
            self.assertEqual(expected, rc, result + report)
        else:
            rc, report = cmd(['update-alternatives', '--auto', 'iptables'])
            expected = 0
            result = 'Got exit code %d, expected %d\n' % (rc, expected)
            self.assertEqual(expected, rc, result + report)

            rc, report = cmd(['update-alternatives', '--auto', 'ip6tables'])
            expected = 0
            result = 'Got exit code %d, expected %d\n' % (rc, expected)
            self.assertEqual(expected, rc, result + report)


class UfwTestAuto(UfwCommon):
    '''Test ufw (basic functions-- most covered by the test suites)'''
    def setUp(self):
        '''Set up prior to each test_* function'''
        self._setUp()

    def tearDown(self):
        '''Clean up after each test_* function'''
        self._tearDown()

    def _search_status(self, search):
        '''Test search status'''
        rc, report = cmd(['ufw', 'status', 'verbose'])
        expected = 0
        result = 'Got exit code %d, expected %d\n' % (rc, expected)
        self.assertEqual(expected, rc, result + report)
        self.assertTrue(search in report,
                        "Could not find '%s' in:\n%s" % (search, report))

    def _enable(self):
        '''Enable the firewall'''
        args = ['ufw']
        args.append('--force')
        args.append('enable')

        rc, report = cmd(args)
        expected = 0
        result = 'Got exit code %d, expected %d\n' % (rc, expected)
        self.assertEqual(expected, rc, result + report)
        search = 'Status: active'
        self._search_status(search)

    def _disable(self):
        '''Disable the firewall'''
        rc, report = cmd(['ufw', 'disable'])
        expected = 0
        result = 'Got exit code %d, expected %d\n' % (rc, expected)
        self.assertEqual(expected, rc, result + report)
        search = 'Status: inactive'
        self._search_status(search)

    def test_enable_disable(self):
        '''Test enable/disable'''
        self._enable()
        self._disable()

    def test_service(self):
        '''Test service/proto'''
        self._enable()

        rc, report = cmd(['ufw', 'allow', 'ssh/tcp'])
        expected = 0
        result = 'Got exit code %d, expected %d\n' % (rc, expected)
        self.assertEqual(expected, rc, result + report)
        search = '22/tcp'
        self._search_status(search)

    def test_logging(self):
        '''Test logging'''
        self._enable()

        rc, report = cmd(['ufw', 'logging', 'on'])
        expected = 0
        result = 'Got exit code %d, expected %d\n' % (rc, expected)
        self.assertEqual(expected, rc, result + report)
        search = "Logging enabled"
        self.assertTrue(search in report,
                        "Could not find '%s' in:\n%s" % (search, report))

        search = 'Logging: on'
        self._search_status(search)

        rc, report = cmd(['ufw', 'logging', 'off'])
        expected = 0
        result = 'Got exit code %d, expected %d\n' % (rc, expected)
        self.assertEqual(expected, rc, result + report)
        search = "Logging disabled"
        self.assertTrue(search in report,
                        "Could not find '%s' in:\n%s" % (search, report))

        search = 'Logging: off'
        self._search_status(search)

    def test_requirements(self):
        rc, report = cmd(['/usr/share/ufw/check-requirements', '-f'])
        expected = 0
        result = 'Got exit code %d, expected %d\n' % (rc, expected)
        self.assertEqual(expected, rc, result + report)


class UfwTestNft(UfwTestAuto):
    '''Test ufw - nft'''
    def setUp(self):
        '''Set up prior to each test_* function'''
        self._setUp()
        self._update_alternatives("nft")


class UfwTestLegacy(UfwTestAuto):
    '''Test ufw - legacy'''
    def setUp(self):
        '''Set up prior to each test_* function'''
        self._setUp()
        self._update_alternatives("legacy")


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == "--container":
        rc, res = cmd(["uname", "-m"])
        if res.strip() == "x86_64":
            running_in_container = True
            print("Adjusting tests for x86_64 container")
        else:
            print("Skipping running tests in non-x86_64 container")
            sys.exit(0)

    suite = unittest.TestSuite()
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(UfwTestAuto))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(UfwTestNft))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(UfwTestLegacy))
    ret = unittest.TextTestRunner(verbosity=2).run(suite)
    if not ret.wasSuccessful():
        sys.exit(1)
