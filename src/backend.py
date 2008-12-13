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
from ufw.common import UFWError, config_dir, UFWRule
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
            except Exception:
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

        # Now that the files are written out, update value in memory
        self.defaults[opt.lower()] = value.lower().strip('"\'')

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

    def get_app_rules_from_template(self, template):
        '''Return a list of UFWRules based on the template rule'''
        rules = []
        profile_names = self.profiles.keys()

        if template.dport in profile_names and template.sport in profile_names:
            dports = ufw.applications.get_ports(self.profiles[template.dport])
            sports = ufw.applications.get_ports(self.profiles[template.sport])
            for i in dports:
                tmp = template.dup_rule()
                tmp.dapp = ""
                tmp.set_port("any", "src")
                try:
                    (port, proto) = ufw.util.parse_port_proto(i)
                    tmp.set_protocol(proto)
                    tmp.set_port(port, "dst")
                except Exception:
                    raise

                tmp.dapp = template.dapp

                if template.dport == template.sport:
                    # Just use the same ports as dst for src when they are the
                    # same to avoid duplicate rules
                    tmp.sapp = ""
                    try:
                        (port, proto) = ufw.util.parse_port_proto(i)
                        tmp.set_protocol(proto)
                        tmp.set_port(port, "src")
                    except Exception:
                        raise

                    tmp.sapp = template.sapp
                    rules.append(tmp)
                else:
                    for j in sports:
                        rule = tmp.dup_rule()
                        rule.sapp = ""
                        try:
                            (port, proto) = ufw.util.parse_port_proto(j)
                            rule.set_protocol(proto)
                            rule.set_port(port, "src")
                        except Exception:
                            raise

                        if rule.protocol == "any":
                            rule.set_protocol(tmp.protocol)

                        rule.sapp = template.sapp
                        rules.append(rule)
        elif template.sport in profile_names:
            for p in ufw.applications.get_ports(self.profiles[template.sport]):
                rule = template.dup_rule()
                rule.sapp = ""
                try:
                    (port, proto) = ufw.util.parse_port_proto(p)
                    rule.set_protocol(proto)
                    rule.set_port(port, "src")
                except Exception:
                    raise

                rule.sapp = template.sapp
                rules.append(rule)
        elif template.dport in profile_names:
            for p in ufw.applications.get_ports(self.profiles[template.dport]):
                rule = template.dup_rule()
                rule.dapp = ""
                try:
                    (port, proto) = ufw.util.parse_port_proto(p)
                    rule.set_protocol(proto)
                    rule.set_port(port, "dst")
                except Exception:
                    raise

                rule.dapp = template.dapp
                rules.append(rule)

        if len(rules) < 1:
            err_msg = _("No rules found for application profile")
            raise UFWError(err_msg)

        return rules

    def update_app_rule(self, profile):
        '''Update rule for profile in place. Returns result string and bool
           on whether or not the profile is used in the current ruleset.
        '''
        updated_rules = []
        updated_rules6 = []
        last_tuple = ""
        rstr = ""
        updated_profile = False

        # Remember, self.rules is from user[6].rules, and not the running
        # firewall.
        for r in self.rules + self.rules6:
            if r.dapp == profile or r.sapp == profile:
                # We assume that the rules are in app rule order. Specifically,
                # if app rule has multiple rules, they are one after the other.
                # If the rule ordering changes, the below will have to change.
                tuple = r.get_app_tuple()
                if tuple == last_tuple:
                    # Skip the rule if seen this tuple already (ie, it is part
                    # of a known tuple).
                    continue
                else:
                    # Have a new tuple, so find and insert new app rules here
                    template = r.dup_rule()
                    template.set_protocol("any")
                    if template.dapp != "":
                        template.set_port(template.dapp, "dst")
                    if template.sapp != "":
                        template.set_port(template.sapp, "src")
                    try:
                        new_app_rules = self.get_app_rules_from_template(\
                                          template)
                    except Exception:
                        raise

                    for new_r in new_app_rules:
                        new_r.normalize()
                        if new_r.v6:
                            updated_rules6.append(new_r)
                        else:
                            updated_rules.append(new_r)

                    last_tuple = tuple
                    updated_profile = True
            else:
                if r.v6:
                    updated_rules6.append(r)
                else:
                    updated_rules.append(r)

        if updated_profile:
            self.rules = updated_rules
            self.rules6 = updated_rules6
            rstr += _("Rules updated for profile '%s'") % (profile)

            try:
                self._write_rules(False) # ipv4
                self._write_rules(True) # ipv6
            except Exception:
                err_msg = _("Couldn't update application rules")
                raise UFWError(err_msg)

        return (rstr, updated_profile)

    def find_application_name(self, str):
        '''Find the application profile name for str'''
        if self.profiles.has_key(str):
            return str

        match = ""
        matches = 0
        for n in self.profiles.keys():
            if n.lower() == str.lower():
                match = n
                matches += 1

        debug_msg = "'%d' matches for '%s'" % (matches, str)
        debug(debug_msg)
        if matches == 1:
            return match
        elif matches > 1:
            err_msg = _("Found multiple matches for '%s'. Please use exact profile name") % (str)
        err_msg = _("Could not find a profile matching '%s'") % (str)
        raise UFWError(err_msg)

    # API overrides
    def get_loglevel(self):
        raise UFWError("UFWBackend.get_loglevel: need to override")

    def set_loglevel(self, level):
        raise UFWError("UFWBackend.set_loglevel: need to override")

    def get_default_policy(self):
        raise UFWError("UFWBackend.get_default_policy: need to override")

    def set_default_policy(self, policy):
        raise UFWError("UFWBackend.set_default_policy: need to override")

    def get_status_raw(self):
        raise UFWError("UFWBackend.get_status_raw: need to override")

    def get_status(self):
        raise UFWError("UFWBackend.get_status: need to override")

    def set_rule(self, rule, allow_reload):
        raise UFWError("UFWBackend.set_rule: need to override")

    def start_firewall(self):
        raise UFWError("UFWBackend.start_firewall: need to override")

    def stop_firewall(self):
        raise UFWError("UFWBackend.stop_firewall: need to override")

    def get_app_rules_from_system(self, template, v6):
        raise UFWError("UFWBackend.get_app_rules_from_system: need to " + \
                       "override")

