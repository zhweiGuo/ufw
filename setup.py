#
# ufw: front-end for Linux firewalling
#
# Copyright 2008-2009 Canonical Ltd.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License version 3,
#    as published by the Free Software Foundation.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

# Install with:
# python ./setup.py install --root="/tmp/ufw"

from distutils.command.install import install as _install
from distutils.core import setup
import errno
import os
import re
import sys
import shutil
import subprocess

ufw_version = '0.29'

def cmd(command):
    '''Try to execute the given command.'''
    try:
        sp = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    except OSError, e:
        return [127, str(e)]

    out = sp.communicate()[0]
    return [sp.returncode,out]

class Install(_install, object):
    '''Override distutils to install the files where we want them.'''
    def run(self):
        if self.home != None and self.root != None:
            print "Don't specify --home and --root at same time"
            return

        real_confdir = os.path.join('/etc')
        real_statedir = os.path.join('/lib', 'ufw')
        real_transdir = os.path.join('/var', 'lib', 'ufw')
        real_prefix = self.prefix
        if self.home != None:
            real_confdir = self.home + real_confdir
            real_statedir = self.home + real_statedir
            real_transdir = self.home + real_transdir
            real_prefix = self.home + '/usr'

        # Update the modules' paths
        for file in [ 'common.py' ]:
            print "Updating " + file
            subprocess.call(["sed",
                             "-i",
                             "s%#CONFIG_PREFIX#%" + real_confdir + "%g",
                             os.path.join('staging', file)])

            subprocess.call(["sed",
                             "-i",
                             "s%#STATE_PREFIX#%" + real_statedir + "%g",
                             os.path.join('staging', file)])

            subprocess.call(["sed",
                             "-i",
                             "s%#PREFIX#%" + real_prefix + "%g",
                             os.path.join('staging', file)])

            subprocess.call(["sed",
                             "-i",
                             "s%#IPTABLES_DIR#%" + iptables_dir + "%g",
                             os.path.join('staging', file)])

        # Now byte-compile everything
        super(Install, self).run()

        # Install script and data files
        prefix = real_prefix
        if self.root != None:
            prefix = self.root + real_prefix

        script = os.path.join(prefix, 'sbin', 'ufw')
        manpage = os.path.join(prefix, 'share', 'man', 'man8', 'ufw.8')
        manpage_f = os.path.join(prefix, 'share', 'man', 'man8', \
                                 'ufw-framework.8')

        for f in [ script, manpage, manpage_f ]:
            self.mkpath(os.path.dirname(f))

        self.copy_file('staging/ufw', script)
        self.copy_file('doc/ufw.8', manpage)
        self.copy_file('doc/ufw-rules.8', manpage_f)

        # Install state files and helper scripts
        statedir = real_statedir
        if self.root != None:
            statedir = self.root + real_statedir
        self.mkpath(statedir)

        user_rules = os.path.join(statedir, 'user.rules')
        user6_rules = os.path.join(statedir, 'user6.rules')
        self.copy_file('conf/user.rules', user_rules)
        self.copy_file('conf/user6.rules', user6_rules)

        init_helper = os.path.join(statedir, 'ufw-init')
        init_helper_functions = os.path.join(statedir, 'ufw-init-functions')
        self.copy_file('src/ufw-init', init_helper)
        self.copy_file('src/ufw-init-functions', init_helper_functions)

        # Install translations
        transdir = real_transdir
        if self.root != None:
            transdir = self.root + real_transdir
        i18ndir = os.path.join(transdir, 'messages')
        self.mkpath(i18ndir)
        self.copy_tree('po', i18ndir)

        # Install configuration files
        confdir = real_confdir
        if self.root != None:
            confdir = self.root + real_confdir

        defaults = os.path.join(confdir, 'default', 'ufw')
        ufwconf = os.path.join(confdir, 'ufw', 'ufw.conf')
        sysctl = os.path.join(confdir, 'ufw', 'sysctl.conf')
        before_rules = os.path.join(confdir, 'ufw', 'before.rules')
        after_rules = os.path.join(confdir, 'ufw', 'after.rules')
        before6_rules = os.path.join(confdir, 'ufw', 'before6.rules')
        after6_rules = os.path.join(confdir, 'ufw', 'after6.rules')
        apps_dir = os.path.join(confdir, 'ufw', 'applications.d')

        for f in [ defaults, ufwconf ]:
            self.mkpath(os.path.dirname(f))

        self.mkpath(apps_dir)

        self.copy_file('conf/ufw.defaults', defaults)
        self.copy_file('conf/ufw.conf', ufwconf)
        self.copy_file('conf/sysctl.conf', sysctl)
        self.copy_file('conf/before.rules', before_rules)
        self.copy_file('conf/after.rules', after_rules)
        self.copy_file('conf/before6.rules', before6_rules)
        self.copy_file('conf/after6.rules', after6_rules)

        # Update the installed rules files' permissions
        for file in [ before_rules, after_rules, before6_rules, after6_rules, \
                      user_rules, user6_rules ]:
            os.chmod(file, 0640)

        # Update the installed files' paths
        for file in [ defaults, ufwconf, before_rules, after_rules, \
                      before6_rules, after6_rules, script, \
                      manpage, manpage_f, sysctl, init_helper, \
                      init_helper_functions ]:
            print "Updating " + file
            subprocess.call(["sed",
                             "-i",
                             "s%#CONFIG_PREFIX#%" + real_confdir + "%g",
                             file])

            subprocess.call(["sed",
                             "-i",
                             "s%#PREFIX#%" + real_prefix + "%g",
                             file])

            subprocess.call(["sed",
                             "-i",
                             "s%#STATE_PREFIX#%" + real_statedir + "%g",
                             file])

            subprocess.call(["sed",
                             "-i",
                             "s%#VERSION#%" + ufw_version + "%g",
                             file])

if os.path.exists('staging'):
    shutil.rmtree('staging')
shutil.copytree('src', 'staging')
os.unlink(os.path.join('staging', 'ufw-init'))
os.unlink(os.path.join('staging', 'ufw-init-functions'))

iptables_exe = ''
iptables_dir = ''
found = False
required_binaries = ['iptables', 'ip6tables', 'iptables-restore',
                     'ip6tables-restore']
for dir in ['/sbin', '/bin', '/usr/sbin', '/usr/bin', '/usr/local/sbin', \
            '/usr/local/bin']:
    for e in required_binaries:
        if not os.path.exists(os.path.join(dir, e)):
            break

        if e == required_binaries[-1]:
            found = True
            break
    if found:
        iptables_dir = dir
        iptables_exe = os.path.join(iptables_dir, "iptables")
        break

if not found:
    print >> sys.stderr, "ERROR: could not find all required binaries:" % \
                         (required_binaries)
    sys.exit(1)

(rc, out) = cmd([iptables_exe, '-V'])
if rc != 0:
    raise OSError(errno.ENOENT, "Could not find version for '%s'" % \
                  (iptables_exe))
version = re.sub('^v', '', re.split('\s', out)[1])
print "Found '%s' version '%s'" % (iptables_exe, version)
if version < "1.4":
    print >> sys.stderr, "WARN: version '%s' has limited IPv6 support. See README for details." % (version)

setup (name='ufw',
      version=ufw_version,
      description='front-end for Linux firewalling',
      long_description='front-end for Linux firewalling',
      author='Jamie Strandboge',
      author_email='jamie@canonical.com',
      url='https://launchpad.net/ufw',
      license='GPL-3',
      cmdclass={'install': Install},
      package_dir={'ufw': 'staging'},
      py_modules=['ufw.backend', 'ufw.backend_iptables', 'ufw.common', 'ufw.frontend', 'ufw.util', 'ufw.applications']
)

shutil.rmtree('staging')
