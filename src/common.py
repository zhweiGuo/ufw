#
# common.py: common classes for ufw
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
import socket
import ufw.util
from ufw.util import debug

programName = "ufw"
state_dir = "#STATE_PREFIX#"
config_dir = "#CONFIG_PREFIX#"

class UFWError(Exception):
    '''This class represents ufw exceptions'''
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class UFWRule:
    '''This class represents firewall rules'''
    def __init__(self, action, protocol, dport="any", dst="0.0.0.0/0",
                 sport="any", src="0.0.0.0/0"):
        self.remove = False
        self.v6 = False
        self.dst = ""
        self.src = ""
        try:
            self.set_action(action)
            self.set_protocol(protocol)
            self.set_port(dport)
            self.set_port(sport, "src")
            self.set_src(src)
            self.set_dst(dst)
        except UFWError:
            raise

    def __str__(self):
        print self.format_rule()

    def format_rule(self):
        '''Format rule for for later parsing'''
        str = ""

        # Protocol is handled below
        if self.protocol == "any":
            str = " -p all"
        else:
            str = " -p " + self.protocol

        if self.dst != "0.0.0.0/0" and self.dst != "::/0":
            str += " -d " + self.dst
        if self.dport != "any":
            str += " --dport " + self.dport
        if self.src != "0.0.0.0/0" and self.src != "::/0":
            str += " -s " + self.src
        if self.sport != "any":
            str += " --sport " + self.sport
        if self.action == "allow":
            str += " -j ACCEPT"
        else:
            str += " -j DROP"

        return str.strip()

    def set_action(self, action):
        '''Sets action of the rule'''
        if action.lower() == "allow":
            self.action = action
        else:
            self.action = "deny"

    def set_port(self, port, loc="dst"):
        '''Sets port and location (destination or source) of the rule'''
        err_msg = _("Bad port '%s'") % (port)
        if port == "any":
            pass
        elif re.match('^\d+$', port):
            if int(port) < 1 or int(port) > 65535:
                raise UFWError(err_msg)
        elif re.match(r'^\w[\w\-]+', port):
            try:
                port = socket.getservbyname(port)
            except Exception, (error):
                raise UFWError(err_msg)
        else:
            raise UFWError(err_msg)

        if loc == "src":
            self.sport = str(port)
        else:
            self.dport = str(port)

    def set_protocol(self, protocol):
        '''Sets protocol of the rule'''
        if protocol == "tcp" or protocol == "udp" or protocol == "any":
            self.protocol = protocol
        else:
            err_msg = _("Unsupported protocol '%s'") % (protocol)
            raise UFWError(err_msg)

    def _fix_anywhere(self):
        '''Adjusts src and dst based on v6'''
        if self.v6:
            if self.dst and (self.dst == "any" or self.dst == "0.0.0.0/0"):
                self.dst = "::/0"
            if self.src and (self.src == "any" or self.src == "0.0.0.0/0"):
                self.src = "::/0"
        else:
            if self.dst and (self.dst == "any" or self.dst == "::/0"):
                self.dst = "0.0.0.0/0"
            if self.src and (self.src == "any" or self.src == "::/0"):
                self.src = "0.0.0.0/0"

    def set_v6(self, v6):
        '''Sets whether this is ipv6 rule, and adjusts src and dst 
           accordingly.
        '''
        self.v6 = v6
        self._fix_anywhere()

    def set_src(self, addr):
        '''Sets source address of rule'''
        tmp = addr.lower()

        if tmp != "any" and not ufw.util.valid_address(tmp) and \
           not ufw.util.valid_address(tmp, True):
            err_msg = _("Bad source address")
            raise UFWError(err_msg)
        self.src = tmp
        self._fix_anywhere()

    def set_dst(self, addr):
        '''Sets destination address of rule'''
        tmp = addr.lower()

        if tmp != "any" and not ufw.util.valid_address(tmp) and \
           not ufw.util.valid_address(tmp, True):
            err_msg = _("Bad destination address")
            raise UFWError(err_msg)
        self.dst = tmp
        self._fix_anywhere()

    def match(x, y):
        '''Check if rules match
        Return codes:
          0  match
          1  no match
         -1  match all but action
        '''
        dbg_msg = _("No match")
        if x.dport != y.dport:
            debug(dbg_msg)
            return 1
        if x.sport != y.sport:
            debug(dbg_msg)
            return 1
        if x.protocol != y.protocol:
            debug(dbg_msg)
            return 1
        if x.src != y.src:
            debug(dbg_msg)
            return 1
        if x.dst != y.dst:
            debug(dbg_msg)
            return 1
        if x.v6 != y.v6:
            debug(dbg_msg)
            return 1
        
        if x.action == y.action:
            dbg_msg = _("Found exact match")
            debug(dbg_msg)
            return 0
        dbg_msg = _("Found opposite match")
        debug(dbg_msg)
        return -1

