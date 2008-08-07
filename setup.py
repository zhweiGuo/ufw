#
# ufw: front-end for Linux firewalling
#
# Copyright (C) 2008 Canonical Ltd.
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
import os
from popen2 import Popen3
import sys
import shutil

ufw_version = '0.20'

class Install(_install, object):
    '''Override distutils to install the files where we want them.'''
    def run(self):
        if self.home != None and self.root != None:
            print "Don't specify --home and --root at same time"
            return

        real_confdir = os.path.join('/etc')
        real_statedir = os.path.join('/var', 'lib', 'ufw')
        real_prefix = self.prefix
        if self.home != None:
            real_confdir = self.home + real_confdir
            real_statedir = self.home + real_statedir
            real_prefix = self.home + '/usr'

        # Update the modules' paths
        for file in [ 'common.py' ]:
            print "Updating " + file
            a = Popen3("sed -i 's%#CONFIG_PREFIX#%" + real_confdir + "%g' " + \
                       os.path.join('staging', file))
            while a.poll() == -1:
                pass

            a = Popen3("sed -i 's%#STATE_PREFIX#%" + real_statedir + "%g' " + \
                       os.path.join('staging', file))
            while a.poll() == -1:
                pass

        # Now byte-compile everything
        super(Install, self).run()

        # Install script and data files
        prefix = real_prefix
        if self.root != None:
            prefix = self.root + real_prefix

        script = os.path.join(prefix, 'sbin', 'ufw')
        manpage = os.path.join(prefix, 'share', 'man', 'man8', 'ufw.8')

        for dir in [ script, manpage ]:
            self.mkpath(os.path.dirname(dir))
        
        self.copy_file('staging/ufw', script)
        self.copy_file('doc/ufw.8', manpage)

        # Install state files
        statedir = real_statedir
        if self.root != None:
            statedir = self.root + real_statedir

        user_rules = os.path.join(statedir, 'user.rules')
        user6_rules = os.path.join(statedir, 'user6.rules')
        self.mkpath(statedir)
        self.copy_file('conf/user.rules', user_rules)
        self.copy_file('conf/user6.rules', user6_rules)

        # Install translations
        i18ndir = os.path.join(statedir, 'messages')
        self.mkpath(i18ndir)
        self.copy_tree('messages', i18ndir)

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
        initscript = os.path.join(confdir, 'init.d', 'ufw')

        for f in [ defaults, ufwconf, initscript ]:
            self.mkpath(os.path.dirname(f))
        
        self.copy_file('conf/ufw.defaults', defaults)
        self.copy_file('conf/ufw.conf', ufwconf)
        self.copy_file('conf/sysctl.conf', sysctl)
        self.copy_file('conf/before.rules', before_rules)
        self.copy_file('conf/after.rules', after_rules)
        self.copy_file('conf/before6.rules', before6_rules)
        self.copy_file('conf/after6.rules', after6_rules)
        self.copy_file('conf/initscript', initscript)

        # Update the installed files' paths
        for file in [ defaults, ufwconf, before_rules, after_rules, \
                      before6_rules, after6_rules, initscript, script, \
                      manpage, sysctl ]:
            print "Updating " + file
            a = Popen3("sed -i 's%#CONFIG_PREFIX#%" + real_confdir + "%g' " + file)
            while a.poll() == -1:
                pass

            a = Popen3("sed -i 's%#PREFIX#%" + real_prefix + "%g' " + file)
            while a.poll() == -1:
                pass
        
            a = Popen3("sed -i 's%#STATE_PREFIX#%" + real_statedir + "%g' " + file)
            while a.poll() == -1:
                pass

            a = Popen3("sed -i 's%#VERSION#%" + ufw_version + "%g' " + file)
            while a.poll() == -1:
                pass


if os.path.exists('staging'):
    shutil.rmtree('staging')
shutil.copytree('src', 'staging')

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
      py_modules=['ufw.backend', 'ufw.backend_iptables', 'ufw.common', 'ufw.frontend', 'ufw.util']
)

shutil.rmtree('staging')
