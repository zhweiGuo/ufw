#
# util.py: utility functions for ufw
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
import shutil
import socket
import struct
import subprocess
import sys
from tempfile import mkstemp

debugging = False


def get_services_proto(port):
    '''Get the protocol for a specified port from /etc/services'''
    proto = ""
    try:
        socket.getservbyname(port)
    except:
        raise

    try:
        socket.getservbyname(port, "tcp")
        proto = "tcp"
    except:
        pass

    try:
        socket.getservbyname(port, "udp")
        if proto == "tcp":
            proto = "any"
        else:
            proto = "udp"
    except:
        pass

    return proto


def parse_port_proto(str):
    '''Parse port or port and protocol'''
    port = ""
    proto = ""
    tmp = str.split('/')
    if len(tmp) == 1:
        port = tmp[0]
        proto = "any"
    elif len(tmp) == 2:
        port = tmp[0]
        proto = tmp[1]
    else:
        raise ValueError
    return (port, proto)


def valid_address6(addr):
    '''Verifies if valid IPv6 address'''
    if not socket.has_ipv6:
        warn("python does not have IPv6 support.")
        return False

    # quick and dirty test
    if len(addr) > 43 or not re.match(r'^[a-fA-F0-9:\./]+$', addr):
        return False

    net = addr.split('/')
    try:
        socket.inet_pton(socket.AF_INET6, net[0])
    except:
        return False

    if len(net) > 2:
        return False
    elif len(net) == 2:
        # Check netmask specified via '/'
        if not _valid_cidr_netmask(net[1], True):
            return False

    return True


def valid_address4(addr):
    '''Verifies if valid IPv4 address'''
    # quick and dirty test
    if len(addr) > 31 or not re.match(r'^[0-9\./]+$', addr):
        return False

    net = addr.split('/')
    try:
        socket.inet_pton(socket.AF_INET, net[0])
        if not _valid_dotted_quads(net[0], False):
            return False
    except:
        return False

    if len(net) > 2:
        return False
    elif len(net) == 2:
        # Check netmask specified via '/'
        if not valid_netmask(net[1], False):
            return False

    return True


def valid_netmask(nm, v6):
    '''Verifies if valid cidr or dotted netmask'''
    return _valid_cidr_netmask(nm, v6) or _valid_dotted_quads(nm, v6)


#
# valid_address()
#    version="6" tests if a valid IPv6 address
#    version="4" tests if a valid IPv4 address
#    version="any" tests if a valid IP address (IPv4 or IPv6)
#
def valid_address(addr, version="any"):
    '''Validate IP addresses'''
    if version == "6":
        return valid_address6(addr)
    elif version == "4":
        return valid_address4(addr)
    elif version == "any":
        return valid_address4(addr) or valid_address6(addr)

    raise ValueError


def normalize_address(orig, v6):
    '''Convert address to standard form. Use no netmask for IP addresses. If
       If netmask is specified and not all 1's, for IPv4 use cidr if possible, 
       otherwise dotted netmask and for IPv6, use cidr.
    '''
    net = []
    version = "4"
    if v6:
        version = "6"

    if '/' in orig:
        net = orig.split('/')
        # Remove host netmasks
        if v6 and net[1] == "128":
            del net[1]
        elif not v6:
            if net[1] == "32" or net[1] == "255.255.255.255":
                del net[1]
    else:
        net.append(orig)

    if not v6 and len(net) == 2 and _valid_dotted_quads(net[1], v6):
        try:
            net[1] = _dotted_netmask_to_cidr(net[1], v6)
        except:
            # Not valid cidr, so just use the dotted quads
            pass

    addr = net[0]
    if len(net) == 2:
        addr += "/" + net[1]

    if not valid_address(addr, version):
        dbg_msg = "Invalid address '%s'" % (addr)
        debug(dbg_msg)
        raise ValueError

    return addr


def open_file_read(f):
    '''Opens the specified file read-only'''
    try:
        orig = open(f, 'r')
    except Exception:
        raise

    return orig


def open_files(f):
    '''Opens the specified file read-only and a tempfile read-write.'''
    try:
        orig = open_file_read(f)
        (tmp, tmpname) = mkstemp()
    except Exception:
        orig.close()
        raise

    return { "orig": orig, "origname": f, "tmp": tmp, "tmpname": tmpname }


def close_files(fns, update = True):
    '''Closes the specified files (as returned by open_files), and update
       original file with the temporary file.
    '''
    fns['orig'].close()
    os.close(fns['tmp'])

    if update:
        try:
            shutil.copystat(fns['origname'], fns['tmpname'])
            shutil.copy(fns['tmpname'], fns['origname'])
        except Exception:
            raise

    try:
        os.unlink(fns['tmpname'])
    except OSError, e:
        raise


def cmd(command):
    '''Try to execute the given command.'''
    try:
        sp = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    except OSError, e:
        return [127, str(e)]

    out = sp.communicate()[0]
    return [sp.returncode,out]


def cmd_pipe(command1, command2):
    '''Try to pipe command1 into command2.'''
    try:
        sp1 = subprocess.Popen(command1, stdout=subprocess.PIPE)
        sp2 = subprocess.Popen(command2, stdin=sp1.stdout)
    except OSError, e:
        return [127, str(e)]

    out = sp2.communicate()[0]
    return [sp2.returncode,out]


def error(msg, exit=True):
    '''Print error message and exit'''
    print >> sys.stderr, "ERROR: %s" % (msg)
    if exit:
        sys.exit(1)


def warn(msg):
    '''Print warning message'''
    print >> sys.stderr, "WARN: %s" % (msg)


def debug(msg):
    '''Print debug message'''
    if debugging:
        print >> sys.stderr, "DEBUG: %s" % (msg)

#
# Internal helper functions
#
def _valid_cidr_netmask(nm, v6):
    '''Verifies cidr netmasks'''
    num = 32
    if v6:
        num = 128

    if not re.match(r'^[0-9]+$', nm) or int(nm) < 0 or int(nm) > num:
        return False

    return True


def _valid_dotted_quads(nm, v6):
    '''Verifies dotted quad ip addresses and netmasks'''
    if v6:
        return False
    else:
        if re.match(r'^[0-9]+\.[0-9\.]+$', nm):
            quads = re.split('\.', nm)
            if len(quads) != 4:
                return False
            for q in quads:
                if not q or int(q) < 0 or int(q) > 255:
                    return False
        else:
            return False

    return True

#
# _dotted_netmask_to_cidr()
# Returns:
#   cidr integer (0-32 for ipv4 and 0-128 for ipv6)
#
# Raises exception if cidr cannot be found
#
def _dotted_netmask_to_cidr(nm, v6):
    '''Convert netmask to cidr. IPv6 dotted netmasks are not supported.'''
    cidr = ""
    if v6:
        raise ValueError
    else:
        if not _valid_dotted_quads(nm, v6):
            raise ValueError

        mbits = 0
        bits = long(struct.unpack('>L',socket.inet_aton(nm))[0])
        found_one = False
        for n in range(32):
            if (bits >> n) & 1 == 1:
                found_one = True
            else:
                if found_one:
                    mbits = -1
                    break
                else:
                    mbits += 1

        if mbits >= 0 and mbits <= 32:
            cidr = str(32 - mbits)

    if not _valid_cidr_netmask(cidr, v6):
        raise ValueError

    return cidr


#
# _cidr_to_dotted_netmask()
# Returns:
#   dotted netmask string
#
# Raises exception if dotted netmask cannot be found
#
def _cidr_to_dotted_netmask(cidr, v6):
    '''Convert cidr to netmask. IPv6 dotted netmasks not supported.'''
    nm = ""
    if v6:
        raise ValueError
    else:
        if not _valid_cidr_netmask(cidr, v6):
            raise ValueError
        bits = 0L
        for n in range(32):
            if n < int(cidr):
                bits |= 1<<31 - n
        nm = socket.inet_ntoa(struct.pack('>L', bits))

    if not _valid_dotted_quads(nm, v6):
        raise ValueError

    return nm
