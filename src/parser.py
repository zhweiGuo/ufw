#
# parser.py: parser class for ufw
#
# Copyright 2009 Canonical Ltd.
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
#
# Adding New Commands
#
# 1. Create a new UFWCommandFoo object that implements UFWCommand
# 2. Create UFWCommandFoo.parse() to return a UFWParserResponse object
# 3. Create UFWCommandFoo.help() to display help for this command
# 4. Register this command with the parser using:
#    parser.register_command(UFWCommandFoo('foo'))
#
#
# Extending Existing Commands
#
# 1. Register the new command with an existing UFWCommand via
#    register_command(). Eg
#    parser.register_command(UFWCommandCommand('new_command'))
# 2. Update UFWCommandExisting.parse() for new_command
# 3. Update UFWCommandExisting.help() for new_command
#

import re
import ufw.util
from common import UFWError
from ufw.util import debug

import sys

class UFWCommand:
    '''Generic class for parser commands.'''
    def __init__(self, type, command):
        self.command = command
        self.types = []
        if type not in self.types:
            self.types.append(type)
        self.type = type

    def parse(self, argv):
        if len(argv) < 1:
            raise ValueError()

        r = UFWParserResponse(argv[0].lower())
        
        return r

    def help(self, args):
        raise UFWError("UFWCommand.help: need to override")

class UFWCommandRule(UFWCommand):
    '''Class for parsing ufw rule commands'''
    def __init__(self, command):
        type = 'rule'
        UFWCommand.__init__(self, type, command)

    def parse(self, argv):
        action = ""
        rule = ""
        type = ""
        from_type = "any"
        to_type = "any"
        from_service = ""
        to_service = ""
        insert_pos = ""
        logtype = ""

        remove = False
        if len(argv) > 0 and argv[0].lower() == "delete":
            remove = True
            argv.remove(argv[0])
            action = argv[0]

        if len(argv) > 0 and argv[0].lower() == "insert":
            if len(argv) < 4:
                raise ValueError()
            insert_pos = argv[1]

	    # Using position '0' adds rule at end, which is potentially
	    # confusing for the end user
            if insert_pos == "0":
		err_msg = _("Cannot insert rule at position '%s'") % \
                            (insert_pos)
                raise UFWError(err_msg)

            # strip out 'insert NUM' and parse as normal
            del argv[1]
            del argv[0]

            action = argv[0]

        if action == "":
            action = self.command
            argv.insert(0, action)

        if action != "allow" and action != "deny" and action != "reject" and \
           action != "limit":
            raise ValueError()

        nargs = len(argv)
        if nargs < 2:
            raise ValueError()

        # set/strip
        rule_direction = "in"
        if nargs > 2 and (argv[2].lower() == "in" or \
                          argv[2].lower() == "out"):
            rule_direction = argv[2].lower()

        # strip out direction if not an interface rule
        if nargs > 3 and argv[3] != "on" and (argv[2].lower() == "in" or \
                                              argv[2].lower() == "out"):
            rule_direction = argv[2].lower()
            del argv[2]
            nargs = len(argv)

        # strip out 'on' as in 'allow in on eth0 ...'
        has_interface = False
        if nargs > 2 and (argv.count('in') > 0 or argv.count('out') > 0):
            err_msg = _("Invalid interface clause")

            if argv[2].lower() != "in" and argv[2].lower() != "out":
                raise UFWError(err_msg)
            if nargs < 4 or argv[3].lower() != "on":
                raise UFWError(err_msg)

            del argv[3]
            nargs = len(argv)
            has_interface = True

        log_idx = 0
        if has_interface and nargs > 4 and (argv[4].lower() == "log" or \
                                            argv[4].lower() == 'log-all'):
            log_idx = 4
        elif nargs > 3 and (argv[2].lower() == "log" or \
                           argv[2].lower() == 'log-all'):
            log_idx = 2

        if log_idx > 0:
            logtype = argv[log_idx].lower()
            # strip out 'log' or 'log-all' and parse as normal
            del argv[log_idx]
            nargs = len(argv)

        if "log" in argv:
            err_msg = _("Option 'log' not allowed here")
            raise UFWError(err_msg)

        if "log-all" in argv:
            err_msg = _("Option 'log-all' not allowed here")
            raise UFWError(err_msg)

        if nargs < 3 or nargs > 14:
            raise ValueError()

        rule_action = action
        if logtype != "":
            rule_action += "_" + logtype
        rule = ufw.common.UFWRule(rule_action, "any", "any", \
                                  direction=rule_direction)
        if remove:
            rule.remove = remove
        elif insert_pos != "":
            try:
                rule.set_position(insert_pos)
            except Exception:
                raise
        if nargs == 3:
            # Short form where only app or port/proto is given
            if ufw.applications.valid_profile_name(argv[2]):
                # Check if name collision with /etc/services. If so, use
                # /etc/services instead of application profile
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
        elif not 'from' in argv and not 'to' in argv and not 'in' in argv and \
             not 'out' in argv:
            err_msg = _("Need 'to' or 'from' clause")
            raise UFWError(err_msg)
        else:
            # Full form with PF-style syntax
            keys = [ 'proto', 'from', 'to', 'port', 'app', 'in', 'out' ]

            # quick check
            if argv.count("to") > 1 or \
               argv.count("from") > 1 or \
               argv.count("proto") > 1 or \
               argv.count("port") > 2 or \
               argv.count("in") > 1 or \
               argv.count("out") > 1 or \
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
                elif arg == "in" or arg == "out":
                    if i+1 < nargs:
                        try:
                            if arg == "in":
                                rule.set_interface("in", argv[i+1])
                            elif arg == "out":
                                rule.set_interface("out", argv[i+1])
                        except Exception:
                            raise
                    else:
                        err_msg = _("Invalid '%s' clause") % (arg)
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
        if rule and rule.protocol != "any" and \
           (rule.sapp != "" or rule.dapp != ""):
            app = ""
            if rule.dapp:
                app = rule.dapp
            else:
                app = rule.sapp
            err_msg = _("Improper rule syntax ('%s' specified with app rule)") % \
                       (rule.protocol)
            raise UFWError(err_msg)

        r = UFWParserResponse(action)
        r.rule = rule
        r.iptype = type

        return r

class UFWCommandApp(UFWCommand):
    '''Class for parsing ufw application commands'''
    def __init__(self, command):
        type = 'app'
        UFWCommand.__init__(self, type, command)

class UFWCommandBasic(UFWCommand):
    '''Class for parsing ufw basic commands'''
    def __init__(self, command):
        type = 'basic'
        UFWCommand.__init__(self, type, command)

class UFWCommandDefault(UFWCommand):
    '''Class for parsing ufw default commands'''
    def __init__(self, command):
        type = 'default'
        UFWCommand.__init__(self, type, command)

    def parse(self, argv):
        # Basic sanity check
        if len(argv) < 2:
            raise ValueError()

        # Set the direction
        action = ""
        direction = "incoming"
        if len(argv) > 2:
            if argv[2].lower() != "incoming" and argv[2].lower() != "input" and \
               argv[2].lower() != "output" and argv[2].lower() != "outgoing":
                raise ValueError()
            if argv[2].lower().startswith("in"):
                direction = "incoming"
            elif argv[2].lower().startswith("out"):
                direction = "outgoing"
            else:
                direction = argv[2].lower()

        # Set the policy
        if argv[1].lower() == "deny":
            action = "default-deny"
        elif argv[1].lower() == "allow":
            action = "default-allow"
        elif argv[1].lower() == "reject":
            action = "default-reject"
        else:
            raise ValueError()

        action += "-%s" % (direction)

        return UFWParserResponse(action)

class UFWCommandLogging(UFWCommand):
    '''Class for parsing ufw logging commands'''
    def __init__(self, command):
        type = 'logging'
        UFWCommand.__init__(self, type, command)

    def parse(self, argv):
        action = ""
        if len(argv) < 2:
            raise ValueError()
        elif argv[1].lower() == "off":
            action = "logging-off"
        elif argv[1].lower() == "on" or argv[1].lower() == "low" or \
             argv[1].lower() == "medium" or argv[1].lower() == "high" or \
             argv[1].lower() == "full":
            action = "logging-on"
            if argv[1].lower() != "on":
                action += "_" + argv[1].lower()
        else:
            raise ValueError()

        return UFWParserResponse(action)

class UFWCommandStatus(UFWCommand):
    '''Class for parsing ufw status commands'''
    def __init__(self, command):
        type = 'status'
        UFWCommand.__init__(self, type, command)

    def parse(self, argv):
        r = UFWCommand.parse(self, argv)
        if len(argv) > 1:
            if argv[1].lower() == "verbose":
                r.action = "status-verbose"
            elif argv[1].lower() == "numbered":
                r.action = "status-numbered"
        return r

class UFWCommandShow(UFWCommand):
    '''Class for parsing ufw status commands'''
    def __init__(self, command):
        type = 'show'
        UFWCommand.__init__(self, type, command)

    def parse(self, argv):
        action = ""
        if len(argv) == 1:
            raise ValueError()
        elif argv[1].lower() == "raw":
            action = "show-raw"

        return UFWParserResponse(action)

class UFWParserResponse:
    '''Class for ufw parser response'''
    def __init__(self, action):
        self.action = action.lower()
        self.iptype = ""
        self.rule = None

    def __str__(self):
        s = "action='%s'" % (self.action)
        s += ",iptype'%s'" % (self.iptype)
        s += ",rule,'%s'\n" % (self.rule)

        return repr(s)

class UFWParser:
    '''Class for ufw parser'''
    def __init__(self):
        self.commands = {}

    def allowed_command(self, cmd):
        '''Return command if it is allowed, otherwise raise an exception'''
        if cmd.lower() not in self.commands.keys():
            raise ValueError()

        return cmd.lower()

    def parse_command(self, args):
        '''Parse command. Returns a UFWParserAction'''
        dryrun = False
        if len(args) > 0 and args[0].lower() == "--dry-run":
            dryrun = True
            args.remove(args[0])

        try:
            action = self.allowed_command(args[0])
        except Exception:
            err_msg = _("Invalid command '%s'") % (args[0])
            raise UFWError(err_msg)

        cmd = self.commands[action]
        response = cmd.parse(args)
        response.dryrun = dryrun

# all this can go in frontend.parse_command()
#        if cmd.type = 'rule':
#            return (r.action, r.rule, r.type, r.dryrun)
#        elif cmd.type = 'app':
#            return (r.action, r.name, r.dryrun)
#        else:
#            # TODO: clean this up (requires changes to 
#            return (r.action, "", "", "")

        return response
    
    def register_command(self, c):
        key = "%s" % (c.command)
        if self.commands.has_key(key):
            err_msg = _("Command '%s' already exists") % (key)
            raise UFWError(err_msg)
        self.commands[key] = c


if __name__ == "__main__":
    import gettext
    _ = gettext.gettext

# all this in frontend.parse_command()
    p = UFWParser()

    # Basic commands
    for i in ['enable', 'disable', 'help', '--help', 'version', '--version', 'reload']:
        p.register_command(UFWCommandBasic(i))

    # Rule commands
    for i in ['allow', 'limit', 'deny' , 'reject']:
        p.register_command(UFWCommandRule(i))
    p.register_command(UFWCommandRule('insert'))
    p.register_command(UFWCommandRule('delete'))

    # Miscellaneous commands
    p.register_command(UFWCommandDefault('default'))
    p.register_command(UFWCommandLogging('logging'))
    p.register_command(UFWCommandStatus('status'))
    p.register_command(UFWCommandShow('show'))

    print sys.argv
    if len(sys.argv) < 2:
        print >> sys.stderr, "ERROR: not enough args"
        sys.exit(1)

    pr = p.parse_command(sys.argv[1:])
    try:
        pr = p.parse_command(sys.argv[1:])
    except UFWError, e:
        print >> sys.stderr, "ERROR: %s" % (e)
        sys.exit(1)
#    except Exception:
#        print >> sys.stderr, "Invalid syntax"
#        sys.exit(1)

    print pr
