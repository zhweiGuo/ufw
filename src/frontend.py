#
# frontend.py: frontend interface for ufw
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

import re
import sys
import warnings

from ufw.common import UFWError
import ufw.util
from ufw.util import error
from ufw.backend_iptables import UFWBackendIptables

def parse_command(argv):
    '''Parse command. Returns tuple for action, rule, ip_version and dryrun.'''
    action = ""
    rule = ""
    type = ""
    from_type = "any"
    to_type = "any"
    from_service = ""
    to_service = ""
    dryrun = False

    if len(argv) > 1 and argv[1].lower() == "--dry-run":
        dryrun = True
        argv.remove(argv[1])

    remove = False
    if len(argv) > 1 and argv[1].lower() == "delete":
        remove = True
        argv.remove(argv[1])

    nargs = len(argv)

    if nargs < 2:
        raise ValueError()

    allowed_cmds = ['enable', 'disable', 'help', '--help', 'default', \
                    'logging', 'status', 'version', '--version', 'allow', \
                    'deny', 'limit' ]

    if not argv[1].lower() in allowed_cmds:
        raise ValueError()
    else:
        action = argv[1].lower()

    if action == "logging":
        if nargs < 3:
            raise ValueError()
        elif argv[2].lower() == "off":
            action = "logging-off"
        elif argv[2].lower() == "on":
            action = "logging-on"
        else:
            raise ValueError()

    if action == "status":
        if nargs > 2 and argv[2].lower() == "verbose":
            action = "status-verbose"

    if action == "default":
        if nargs < 3:
            raise ValueError()
        elif argv[2].lower() == "deny":
            action = "default-deny"
        elif argv[2].lower() == "allow":
            action = "default-allow"
        else:
            raise ValueError()

    if action == "allow" or action == "deny" or action == "limit":
        if nargs < 3 or nargs > 12:
            raise ValueError()

        rule = ufw.common.UFWRule(action, "any", "any")
        if remove:
            rule.remove = remove
        if nargs == 3:
            # Short form where only app or port/proto is given
            if ufw.applications.valid_profile_name(argv[2]):
                try:
                    ufw.util.get_services_proto(argv[2])
                except Exception:
                    type = "both"
                    rule.dapp = argv[2]
                    rule.set_port(argv[2], "dst")
            if rule.dapp == "":
                try:
                    (port, proto) = ufw.util.parse_port_proto(argv[2])
                except UFWError:
                    err_msg = _("Bad port")
                    raise UFWError(err_msg)

                if not re.match('^\d([0-9,:]*\d+)*$', port):
                    if ',' in port or ':' in port:
                        err_msg = _("Port ranges must be numeric")
                        raise UFWError(err_msg)
                    to_service = port

                try:
                    rule.set_protocol(proto)
                    rule.set_port(port, "dst")
                    type = "both"
                except UFWError:
                    err_msg = _("Bad port")
                    raise UFWError(err_msg)
        elif nargs % 2 != 0:
            err_msg = _("Wrong number of arguments")
            raise UFWError(err_msg)
        elif not 'from' in argv and not 'to' in argv:
            err_msg = _("Need 'to' or 'from' clause")
            raise UFWError(err_msg)
        else:
            # Full form with PF-style syntax
            keys = [ 'proto', 'from', 'to', 'port', 'app' ]

            # quick check
            if argv.count("to") > 1 or \
               argv.count("from") > 1 or \
               argv.count("proto") > 1 or \
               argv.count("port") > 2 or \
               argv.count("app") > 2 or \
               argv.count("app") > 0 and argv.count("proto") > 0:
                err_msg = _("Improper rule syntax")
                raise UFWError(err_msg)

            i = 1
            loc = ""
            for arg in argv[1:]:
                if i % 2 == 0 and argv[i] not in keys:
                    err_msg = _("Invalid token '%s'") % (argv[i])
                    raise UFWError(err_msg)
                if arg == "proto":
                    if i+1 < nargs:
                        try:
                            rule.set_protocol(argv[i+1])
                        except Exception:
                            raise
                    else:
                        err_msg = _("Invalid 'proto' clause")
                        raise UFWError(err_msg)
                elif arg == "from":
                    if i+1 < nargs:
                        try:
                            faddr = argv[i+1].lower()
                            if faddr == "any":
                                faddr = "0.0.0.0/0"
                                from_type = "any"
                            else:
                                if ufw.util.valid_address(faddr, "6"):
                                    from_type = "v6"
                                else:
                                    from_type = "v4"
                            rule.set_src(faddr)
                        except Exception:
                            raise
                        loc = "src"
                    else:
                        err_msg = _("Invalid 'from' clause")
                        raise UFWError(err_msg)
                elif arg == "to":
                    if i+1 < nargs:
                        try:
                            saddr = argv[i+1].lower()
                            if saddr == "any":
                                saddr = "0.0.0.0/0"
                                to_type = "any"
                            else:
                                if ufw.util.valid_address(saddr, "6"):
                                    to_type = "v6"
                                else:
                                    to_type = "v4"
                            rule.set_dst(saddr)
                        except Exception:
                            raise
                        loc = "dst"
                    else:
                        err_msg = _("Invalid 'to' clause")
                        raise UFWError(err_msg)
                elif arg == "port" or arg == "app":
                    if i+1 < nargs:
                        if loc == "":
                            err_msg = _("Need 'from' or 'to' with '%s'") % \
                                        (arg)
                            raise UFWError(err_msg)

                        tmp = argv[i+1]
                        if arg == "app":
                            if loc == "src":
                                rule.sapp = tmp
                            else:
                                rule.dapp = tmp
                        elif not re.match('^\d([0-9,:]*\d+)*$', tmp):
                            if ',' in tmp or ':' in tmp:
                                err_msg = _("Port ranges must be numeric")
                                raise UFWError(err_msg)

                            if loc == "src":
                                from_service = tmp
                            else:
                                to_service = tmp
                        try:
                            rule.set_port(tmp, loc)
                        except Exception:
                            raise
                    else:
                        err_msg = _("Invalid 'port' clause")
                        raise UFWError(err_msg)
                i += 1

            # Figure out the type of rule (IPv4, IPv6, or both) this is
            if from_type == "any" and to_type == "any":
                type = "both"
            elif from_type != "any" and to_type != "any" and \
                 from_type != to_type:
                err_msg = _("Mixed IP versions for 'from' and 'to'")
                raise UFWError(err_msg)
            elif from_type != "any":
                type = from_type
            elif to_type != "any":
                type = to_type

    # Adjust protocol
    if to_service != "" or from_service != "":
        proto = ""
        if to_service != "":
            try:
                proto = ufw.util.get_services_proto(to_service)
            except Exception:
                err_msg = _("Could not find protocol")
                raise UFWError(err_msg)
        if from_service != "":
            if proto == "any" or proto == "":
                try:
                    proto = ufw.util.get_services_proto(from_service)
                except Exception:
                    err_msg = _("Could not find protocol")
                    raise UFWError(err_msg)
            else:
                try:
                    tmp = ufw.util.get_services_proto(from_service)
                except Exception:
                    err_msg = _("Could not find protocol")
                    raise UFWError(err_msg)
                if proto == "any" or proto == tmp:
                    proto = tmp
                elif tmp == "any":
                    pass
                else:
                    err_msg = _("Protocol mismatch (from/to)")
                    raise UFWError(err_msg)

        # Verify found proto with specified proto
        if rule.protocol == "any":
            rule.set_protocol(proto)
        elif proto != "any" and rule.protocol != proto:
            err_msg = _("Protocol mismatch with specified protocol %s") % \
                        (rule.protocol)
            raise UFWError(err_msg)

    # Verify protocol not specified with application rule
    if rule.protocol != "any" and (rule.sapp != "" or rule.dapp != ""):
        app = ""
        if rule.dapp:
            app = rule.dapp
        else:
            app = rule.sapp
        err_msg = _("Protocol '%s' specified with '%s'") % \
                    (rule.protocol, app)
        raise UFWError(err_msg)

    return (action, rule, type, dryrun)


def parse_application_command(argv):
    '''Parse applications command. Returns tuple for action and profile name'''
    name = ""
    action = ""
    dryrun = False

    if len(argv) < 3 or argv[1].lower() != "app":
        raise ValueError()

    argv.remove("app")
    nargs = len(argv)

    if len(argv) > 1 and argv[1].lower() == "--dry-run":
        dryrun = True
        argv.remove(argv[1])

    app_cmds = ['list', 'info', 'default', 'refresh']

    if not argv[1].lower() in app_cmds:
        raise ValueError()
    else:
        action = argv[1].lower()

    if action == "info" or action == "refresh":
        if nargs < 3:
            raise ValueError()
        # Handle quoted name with spaces in it by stripping Python's ['...']
        # list as string text.
        name = str(argv[2]).strip("[']")

    if action == "list" and nargs != 2:
        raise ValueError()

    if action == "default":
        if nargs < 3:
            raise ValueError()
        if argv[2].lower() == "allow":
            action = "default-allow"
        elif argv[2].lower() == "deny":
            action = "default-deny"
        elif argv[2].lower() == "skip":
            action = "default-skip"
        else:
            raise ValueError()

    return (action, name, dryrun)


def get_command_help():
    '''Print help message'''
    msg = _('''
Usage: ''') + ufw.common.programName + _(''' COMMAND

Commands:
  enable			enables the firewall
  disable			disables the firewall
  default ARG			set default policy to ALLOW or DENY
  logging ARG			set logging to ON or OFF
  allow|deny RULE		allow or deny RULE
  delete allow|deny RULE	delete the allow/deny RULE
  status			show firewall status
  version			display version information

Application profile commands:
  app list			list application profiles
  app info PROFILE		show information on PROFILE
  app refresh PROFILE		refresh PROFILE
  app default ARG		set profile policy to ALLOW, DENY or SKIP
''')
    return (msg)


class UFWFrontend:
    '''UI'''
    def __init__(self, dryrun, backend_type="iptables"):
        if backend_type == "iptables":
            try:
                self.backend = UFWBackendIptables(dryrun)
            except Exception:
                raise
        else:
            raise UFWError("Unsupported backend type '%s'" % (backend_type))

    def set_enabled(self, enabled):
        '''Toggles ENABLED state in of <config_dir>/ufw/ufw.conf'''
        res = ""
        try:
            if enabled:
                if not self.backend._is_enabled():
                    self.backend.set_default(self.backend.files['conf'], \
                                             "ENABLED", "yes")
                self.backend.start_firewall()
                res = _("Firewall started and enabled on system startup")
            else:
                if self.backend._is_enabled():
                    self.backend.set_default(self.backend.files['conf'], \
                                             "ENABLED", "no")
                self.backend.stop_firewall()
                res = _("Firewall stopped and disabled on system startup")
        except UFWError, e:
            error(e.value)

        return res

    def set_default_policy(self, policy):
        '''Sets default policy of firewall'''
        res = ""
        try:
            res = self.backend.set_default_policy(policy)
            if self.backend._is_enabled():
                self.backend.stop_firewall()
                self.backend.start_firewall()
        except UFWError, e:
            error(e.value)

        return res

    def set_loglevel(self, level):
        '''Sets log level of firewall'''
        res = ""
        try:
            res = self.backend.set_loglevel(level)
            if self.backend._is_enabled():
                # have to just restart because of ordering of LOG rules
                self.backend.stop_firewall()
                self.backend.start_firewall()
        except UFWError, e:
            error(e.value)

        return res

    def get_status(self, verbose=False):
        '''Shows status of firewall'''
        try:
            out = self.backend.get_status(verbose)
        except UFWError, e:
            error(e.value)

        return out

    def set_rule(self, rule, ip_version):
        '''Updates firewall with rule'''
        res = ""
        try:
            if self.backend.use_ipv6():
                if ip_version == "v4":
                    rule.set_v6(False)
                    res = self.backend.set_rule(rule)
                elif ip_version == "v6":
                    rule.set_v6(True)
                    res = self.backend.set_rule(rule)
                elif ip_version == "both":
                    rule.set_v6(False)
                    res = self.backend.set_rule(rule)
                    rule.set_v6(True)
                    res += "\n" + str(self.backend.set_rule(rule))
                else:
                    err_msg = _("Invalid IP version '%s'") % (ip_version)
                    raise UFWError(err_msg)
            else:
                if ip_version == "v4" or ip_version == "both":
                    rule.set_v6(False)
                    res = self.backend.set_rule(rule)
                elif ip_version == "v6":
                    err_msg = _("IPv6 support not enabled")
                    raise UFWError(err_msg)
                else:
                    err_msg = _("Invalid IP version '%s'") % (ip_version)
                    raise UFWError(err_msg)
        except UFWError, e:
            error(e.value)

        if rule.updated:
            warn_msg = _("Rule changed after normalization")
            warnings.warn(warn_msg)

        return res

    def do_action(self, action, rule, ip_version):
        '''Perform action on rule. action, rule and ip_version are usually
           based on return values from parse_command().
        '''
        res = ""
        if action == "logging-on":
            res = self.set_loglevel("on")
        elif action == "logging-off":
            res = self.set_loglevel("off")
        elif action == "default-allow":
            res = self.set_default_policy("allow")
        elif action == "default-deny":
            res = self.set_default_policy("deny")
        elif action == "status":
            res = self.get_status()
        elif action == "status-verbose":
            res = self.get_status(True)
        elif action == "enable":
            res = self.set_enabled(True)
        elif action == "disable":
            res = self.set_enabled(False)
        elif action == "allow" or action == "deny" or action == "limit":
            if rule.dapp != "" or rule.sapp != "":
                try:
                    rules = self.backend.get_rules_for_apps(rule)
                except Exception:
                    raise
                for r in rules:
                    try:
                        res += self.set_rule(r, ip_version) + '\n'
                    except Exception:
                        print "TODO: undo the currently committed actions if error"
                        raise
            else:
                res = self.set_rule(rule, ip_version)
        else:
            err_msg = _("Unsupported action '%s'") % (action)
            raise UFWError(err_msg)

        return res

    def set_default_application_policy(self, policy):
        '''Sets default application policy of firewall'''
        res = ""
        try:
            res = self.backend.set_default_application_policy(policy)
        except UFWError, e:
            error(e.value)

        return res

    def get_application_list(self):
        '''Display list of known application profiles'''
        names = self.backend.profiles.keys()
        names.sort()
        rstr = _("Available applications:")
        for n in names:
            rstr += "\n  %s" % (n)
        return rstr

    def get_application_info(self, pname):
        '''Display information on profile'''
        names = []
        if pname == "all":
            names = self.backend.profiles.keys()
            names.sort()
        else:
            if not ufw.applications.valid_profile_name(pname):
                err_msg = _("Invalid profile name")
                raise UFWError(err_msg)
            names.append(pname)

        rstr = ""
        for name in names:
            if not self.backend.profiles.has_key(name) or \
               not self.backend.profiles[name]:
                err_msg = _("Could not find profile '%s'") % (name)
                raise UFWError(err_msg)

            if not ufw.applications.verify_profile(name, \
               self.backend.profiles[name]):
                err_msg = _("Invalid profile")
                raise UFWError(err_msg)

            rstr += _("Profile: %s\n") % (name)
            rstr += _("Title: %s\n") % (ufw.applications.get_title(\
                                        self.backend.profiles[name]))

            rstr += _("Description: %s\n\n") % \
                                            (ufw.applications.get_description(\
                                             self.backend.profiles[name]))

            ports = ufw.applications.get_ports(self.backend.profiles[name])
            if len(ports) > 1 or ',' in ports[0]:
                rstr += _("Ports:")
            else:
                rstr += _("Port:")

            for p in ports:
                rstr += "\n  %s" % (p)

            if name != names[len(names)-1]:
                rstr += "\n\n--\n\n"

        return ufw.util.wrap_text(rstr)

    def application_refresh(self, profile):
        '''Refresh application profile'''
        rstr = "UFWFrontend.application_refresh(%s): TODO" % (profile)
        return rstr

    def do_application_action(self, action, profile):
        '''Perform action on profile. action and profile are usually based on
           return values from parse_applications_command().
        '''
        res = ""
        if action == "default-allow":
            res = self.set_default_application_policy("allow")
        elif action == "default-deny":
            res = self.set_default_application_policy("deny")
        elif action == "default-skip":
            res = self.set_default_application_policy("skip")
        elif action == "list":
            res = self.get_application_list()
        elif action == "info":
            res = self.get_application_info(profile)
        elif action == "refresh":
            res = self.application_refresh(profile)
        else:
            err_msg = _("Unsupported action '%s'") % (action)
            raise UFWError(err_msg)

        return res

