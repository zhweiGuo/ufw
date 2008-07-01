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
import subprocess
import sys
from tempfile import mkstemp

# only needed for UFWError
import ufw.common

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
        err_msg = _("Bad port/protocol")
        raise common.UFWError(err_msg)
    return (port, proto)


def valid_address(addr, v6=False):
    '''Validate IP addresses'''
    if v6 and not socket.has_ipv6:
        warn_msg = _("python does not have IPv6 support.")
        warn(warn_msg)
        return False

    # quick and dirty test
    if len(addr) > 43 or not re.match(r'^[a-fA-F0-9:\./]+$', addr):
        return False

    net = addr.split('/')

    if len(net) > 2:
        return False
    elif len(net) == 2:
        # Check netmask specified via '/'

        if not re.match(r'^[0-9]+$', net[1]):
            # Only allow integer netmasks
            return False

        if v6:
            if int(net[1]) < 0 or int(net[1]) > 128:
                return False
        else:
            if int(net[1]) < 0 or int(net[1]) > 32:
                return False

    try:
        if v6:
            socket.inet_pton(socket.AF_INET6, net[0])
        else:
            socket.inet_pton(socket.AF_INET, net[0])
    except:
        return False
    
    return True

def open_file_read(f):
    '''Opens the specified file read-only'''
    try:
        orig = open(f, 'r')
    except OSError, e:
        err_msg = _("Couldn't open '%s' for reading") % (f)
        raise common.UFWError(err_msg)
    except Exception:
        raise

    return orig


def open_files(f):
    '''Opens the specified file read-only and a tempfile read-write.'''
    orig = open_file_read(f)

    try:
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


def error(msg):
    '''Print error message and exit'''
    print >> sys.stderr, _("ERROR: %s") % (msg)
    sys.exit(1)


def warn(msg):
    '''Print warning message'''
    print >> sys.stderr, _("WARN: %s") % (msg)


def debug(msg):
    '''Print debug message'''
    if debugging:
        print >> sys.stderr, _("DEBUG: %s") % (msg)

