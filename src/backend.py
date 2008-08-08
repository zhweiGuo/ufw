#
# backend.py: interface for backends
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

import os
import re
import stat
from stat import *
import sys
import ufw.util
from ufw.util import warn, debug
from ufw.common import UFWError, config_dir
import ufw.applications

class UFWBackend:
    '''Interface for backends'''
    def __init__(self, name, d, extra_files={}):
        self.defaults = {}
        self.name = name
        self.dryrun = d
        self.rules = []
        self.rules6 = []

        self.files = {'defaults': os.path.join(config_dir, 'default/ufw'),
                      'conf': os.path.join(config_dir, 'ufw/ufw.conf'),
                      'apps': os.path.join(config_dir, 'ufw/applications.d') }
        self.files.update(extra_files)

        self.do_checks = True
        try:
            self._do_checks()
            self._get_defaults()
            self._read_rules()
        except Exception:
            raise

        self.profiles = ufw.applications.get_profiles(self.files['apps'])

    def _is_enabled(self):
        if self.defaults.has_key('enabled') and \
           self.defaults['enabled'] == 'yes':
            return True
        return False

    def use_ipv6(self):
        if self.defaults.has_key('ipv6') and \
           self.defaults['ipv6'] == 'yes' and \
           os.path.exists("/proc/sys/net/ipv6"):
            return True
        return False

    def _do_checks(self):
        '''Perform basic security checks:
        is setuid or setgid (for non-Linux systems)
        checks that script is owned by root
        checks that every component in absolute path are owned by root
        checks that every component of absolute path are not a symlink
        warn if script is group writable
        warn if part of script path is group writable

        Doing this at the beginning causes a race condition with later
        operations that don't do these checks.  However, if the user running
        this script is root, then need to be root to exploit the race 
        condition (and you are hosed anyway...)
        '''

        if not self.do_checks:
            err_msg = _("Checks disabled")
            warn(err_msg)
            return True

        # Not needed on Linux, but who knows the places we will go...
        if os.getuid() != os.geteuid():
            err_msg = _("ERROR: this script should not be SUID")
            raise UFWError(err_msg)
        if os.getgid() != os.getegid():
            err_msg = _("ERROR: this script should not be SGID")
            raise UFWError(err_msg)
        uid = os.getuid()

        if uid != 0:
            err_msg = _("You need to be root to run this script")
            raise UFWError(err_msg)

        # Use these so we only warn once
        warned_world_write = {}
        warned_group_write = {}
        warned_owner = {}

        pat = re.compile(r'^\.')

        profiles = []
        if not os.path.isdir(self.files['apps']):
            warn_msg = _("'%s' does not exist") % (self.files['apps'])
            warn(warn_msg)
        else:
            for profile in os.listdir(self.files['apps']):
                profiles.append(os.path.join(self.files['apps'], profile))

        for path in self.files.values() + [ os.path.abspath(sys.argv[0]) ] + \
                profiles:
            while True:
                debug("Checking " + path)
                if pat.search(os.path.basename(path)):
                    err_msg = _("found hidden directory in path: %s") % (path)
                    raise UFWError(err_msg)

                if path == self.files['apps'] and \
                           not os.path.isdir(self.files['apps']):
                    break

                try:
                    statinfo = os.stat(path)
                    mode = statinfo[ST_MODE]
                except OSError, e:
                    err_msg = _("Couldn't stat '%s'") % (path)
                    raise UFWError(err_msg)
                except Exception:
                    raise

                if os.path.islink(path):
                    err_msg = _("found symbolic link in path: %s") % (path)
                    raise UFWError(err_msg)
                if statinfo.st_uid != 0 and not warned_owner.has_key(path):
                    warn_msg = _("uid is %s but '%s' is owned by %s") % \
                                (str(uid), path, str(statinfo.st_uid))
                    warn(warn_msg)
                    warned_owner[path] = True
                if mode & S_IWOTH and not warned_world_write.has_key(path):
                    warn_msg = _("%s is world writable!") % (path)
                    warn(warn_msg)
                    warned_world_write[path] = True
                if mode & S_IWGRP and not warned_group_write.has_key(path):
                    warn_msg = _("%s is group writable!") % (path)
                    warn(warn_msg)
                    warned_group_write[path] = True

                if path == "/":
                    break

                path = os.path.dirname(path)
                if not path:
                    raise

        for f in self.files:
            if f != 'apps' and not os.path.isfile(self.files[f]):
                err_msg = _("'%s' file '%s' does not exist") % (f, \
                                                                self.files[f])
                raise UFWError(err_msg)

    def _get_defaults(self):
        '''Get all settings from defaults file'''
        self.defaults = {}
        for f in [self.files['defaults'], self.files['conf']]:
            try:
                orig = ufw.util.open_file_read(f)
            except:
                err_msg = _("Couldn't open '%s' for reading") % (f)
                raise UFWError(err_msg)
            pat = re.compile(r'^\w+="?\w+"?')
            for line in orig:
                if pat.search(line):
                    tmp = re.split(r'=', line.strip())
                    self.defaults[tmp[0].lower()] = tmp[1].lower().strip('"\'')

            orig.close()

    def set_default(self, f, opt, value):
        '''Sets option in defaults file'''
        if not re.match(r'^[\w_]+$', opt):
            err_msg = _("Invalid option")
            raise UFWError(err_msg)

        try:
            fns = ufw.util.open_files(f)
        except Exception:
            raise
        fd = fns['tmp']

        pat = re.compile(r'^' + opt + '=')
        for line in fns['orig']:
            if pat.search(line):
                os.write(fd, opt + "=" + value + "\n")
            else:
                os.write(fd, line)

        ufw.util.close_files(fns)

    def set_default_application_policy(self, policy):
        '''Sets default application policy of firewall'''
        if not self.dryrun:
            if policy == "allow":
                self.set_default(self.files['defaults'], \
                                            "DEFAULT_APPLICATION_POLICY", \
                                            "\"ACCEPT\"")
            elif policy == "deny":
                self.set_default(self.files['defaults'], \
                                            "DEFAULT_APPLICATION_POLICY", \
                                            "\"DROP\"")
            elif policy == "skip":
                self.set_default(self.files['defaults'], \
                                            "DEFAULT_APPLICATION_POLICY", \
                                            "\"SKIP\"")
            else:
                err_msg = _("Unsupported policy '%s'") % (policy)
                raise UFWError(err_msg)

        rstr = _("Default application policy changed to '%s'\n") % (policy)

        return rstr

    # API overrides
    def get_loglevel(self):
        raise UFWError("UFWBackend.get_loglevel: need to override")

    def set_loglevel(self, level):
        raise UFWError("UFWBackend.set_loglevel: need to override")

    def get_default_policy(self):
        raise UFWError("UFWBackend.get_default_policy: need to override")

    def set_default_policy(self, policy):
        raise UFWError("UFWBackend.set_default_policy: need to override")

    def get_status(self):
        raise UFWError("UFWBackend.get_status: need to override")

    def set_rule(self, rule):
        raise UFWError("UFWBackend.set_rule: need to override")

    def start_firewall(self):
        raise UFWError("UFWBackend.start_firewall: need to override")

    def stop_firewall(self):
        raise UFWError("UFWBackend.stop_firewall: need to override")


