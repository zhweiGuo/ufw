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
# run_unittest() inspired by Lib/test/support.py from Python 3.1
# Copyright (c) 2001-2010 Python Software Foundation; All Rights Reserved

import unittest
import os
import subprocess
import sys
_ = None

topdir = "./tests/unit/tmp"

class Error(Exception):
    '''Error'''


class TestFailed(Error):
    '''Test failed'''


def skipped(cls, s):
    '''Test skipped'''
    # TODO: fix newline
    # TODO: somehow flag and count this as skipped
    print("skipped: %s" % s)
    return False


def recursive_rm(dirPath, contents_only=False):
    '''recursively remove directory'''
    names = os.listdir(dirPath)
    for name in names:
        path = os.path.join(dirPath, name)
        if os.path.islink(path) or not os.path.isdir(path):
            os.unlink(path)
        else:
            recursive_rm(path)
    if contents_only == False:
        os.rmdir(dirPath)


def initvars(install_dir):
    import ufw.common

    global _
    _ = init_gettext()

    if ufw.common.config_dir == "#CONFIG_PREFIX#":
        ufw.common.config_dir = os.path.join(install_dir, "etc", "ufw")


def run_setup():
    global topdir
    install_dir = os.path.join(topdir, "ufw")
    if os.path.exists(topdir):
        recursive_rm(topdir)
    os.mkdir(topdir)
    sp = subprocess.Popen(['python',
                           './setup.py',
                           'install',
                           '--home=%s' % install_dir],
                           stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT,
                           universal_newlines=True)
    sp.communicate()[0]

    return install_dir


def run_unittest(*classes):
    '''Run tests from classes'''
    install_dir = run_setup()

    initvars(install_dir) # initialize ufw for testing

    suite = unittest.TestSuite()
    for cls in classes:
        suite.addTest(unittest.makeSuite(cls))

    runner = unittest.TextTestRunner(sys.stdout, verbosity=2)
    result = runner.run(suite)
    if not result.wasSuccessful():
        if len(result.errors) == 1 and not result.failures:
            err = result.errors[0][1]
        elif len(result.failures) == 1 and not result.errors:
            err = result.failures[0][1]
        else:
            err = "multiple errors occurred"
        raise TestFailed(err)

    if os.path.exists(topdir):
        recursive_rm(topdir)


def init_gettext():
    '''Convenience function to setup _'''

    # This is all stolen from src/ufw
    import gettext
    kwargs = {}
    if sys.version_info[0] < 3:
        # In Python 2, ensure that the _() that gets installed into built-ins
        # always returns unicodes.  This matches the default behavior under
        # Python 3, although that keyword argument is not present in the Python
        # 3 API.
        kwargs['unicode'] = True
    gettext.install("ufw", **kwargs)

    # Internationalization
    gettext.bindtextdomain("ufw", \
                           os.path.join('./locales/mo'))
    gettext.textdomain("ufw")
    try:
        # BAW: I'm not sure why both this and the .install() above is here, but
        # let's roll with it for now.  This is the Python 2 version, which
        # ensures we get unicodes.
        _ = gettext.ugettext
    except AttributeError:
        # Python 3 always returns unicodes.
        _ = gettext.gettext

    return _


def check_for_exception(t, expectedException, func, *args):
    try:
        func(*args)
    except expectedException:
        pass
    except Exception:
        t.fail("Unexpected exception thrown for '%s%s:\n%s" % (str(func), str(args), sys.exc_info()[0]))
    else:
        t.fail('%s not thrown' % str(expectedException))

def get_sample_rule_commands_simple():
    '''Return a list of sample rule commands for simple rules.
       Format:
       [
        [ 'rule', <action>, args... ],
        [ 'rule', <action>, args... ],
       ]
    '''

    cmds = []
    for action in ['allow', 'deny', 'reject', 'limit']:
        for dir in ['', 'in', 'out']:
            for log in ['', 'log', 'log-all']:
                for port in ['', '22', 'tcpmux', 'fsp', 'Apache', 'Samba', \
                             'Apache Full', 'Bind9']:
                    for proto in ['', 'tcp', 'udp']:
                        c = []
                        if dir:
                            c.append(dir)
                            if not port:
                                c.append('on')
                                c.append('eth0')

                        if log:
                            c.append(log)

                        if not port and 'on' in c:
                            # eg, rule allow in on eth0
                            cmds.append(['rule', action] + c)
                            continue

                        try:
                            int(port)
                            if proto:
                                # eg, rule action dir log 22/tcp
                                c.append('%s/%s' % (port, proto))
                            else:
                                # eg, rule action dir log 22
                                c.append(port)
                        except ValueError:
                            if proto or not port:
                                continue
                            else:
                                # eg, rule action dir log Bind9
                                # eg, rule action dir log tcpmux
                                c.append(port)

                        cmds.append(['rule', action] + c)
                        
    return cmds
