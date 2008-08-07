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
        argv.remove("--dry-run")

    remove = False
    if len(argv) > 1 and argv[1].lower() == "delete":
        remove = True
        argv.remove("delete")

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
            # Short form where only port/proto is given
            try:
                (port, proto) = ufw.util.parse_port_proto(argv[2])
                if not re.match('^\d([0-9,:]*\d+)*$', port):
                    to_service = port
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
            keys = [ 'proto', 'from', 'to', 'port' ]

            # quick check
            if argv.count("to") > 1 or \
               argv.count("from") > 1 or \
               argv.count("proto") > 1 or \
               argv.count("port") > 2:
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
                elif arg == "port":
                    if i+1 < nargs:
                        if loc == "":
                            err_msg = _("Need 'from' or 'to' with 'port'")
                            raise UFWError(err_msg)

                        tmp = argv[i+1]
                        if not re.match('^\d([0-9,:]*\d+)*$', tmp):
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
                err_msg = _("Improper rule syntax")
                raise UFWError(err_msg)
        if from_service != "":
            if proto == "any" or proto == "":
                try:
                    proto = ufw.util.get_services_proto(from_service)
                except Exception:
                    err_msg = _("Improper rule syntax")
                    raise UFWError(err_msg)
            else:
                try:
                    tmp = ufw.util.get_services_proto(from_service)
                except Exception:
                    err_msg = _("Improper rule syntax")
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

    return (action, rule, type, dryrun)


def get_command_help():
    '''Print help message'''
    msg = _('''
Usage: ''') + ufw.common.programName + _(''' COMMAND

Commands:
  enable			Enables the firewall
  disable			Disables the firewall
  default ARG			set default policy to ALLOW or DENY
  logging ARG			set logging to ON or OFF
  allow|deny RULE		allow or deny RULE
  delete allow|deny RULE	delete the allow/deny RULE
  status			show firewall status
  version			display version information
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

    def get_status(self):
        '''Shows status of firewall'''
        try:
            out = self.backend.get_status()
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
        elif action == "enable":
            res = self.set_enabled(True)
        elif action == "disable":
            res = self.set_enabled(False)
        elif action == "allow" or action == "deny" or action == "limit":
            res = self.set_rule(rule, ip_version)
        else:
            err_msg = _("Unsupported action '%s'") % (action)
            raise UFWError(err_msg)

        return res

