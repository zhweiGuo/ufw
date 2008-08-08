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

from ConfigParser import *
import os
import re
from stat import *
import ufw.util
from ufw.util import debug, warn

def get_profiles(dir):
    '''Get profiles found in profiles database.  Returns dictionary with
       profile name as key and tuples for fields
    '''
    if not os.path.isdir(dir):
        err_msg = _("Profiles directory does not exist") % (dir)
        raise UFWError("Error: profiles directory does not exist")

    max_size = 10 * 1024 * 1024  # 10MB
    profiles = {}

    files = os.listdir(dir)
    files.sort()

    total_size = 0
    pat = re.compile(r'^\.')
    for f in files:
        abs = dir + "/" + f
        if not os.path.isfile(abs):
            continue

        if pat.search(f):
            warn_msg = _("Skipping '%s': hidden file") % (f)
            warn(warn_msg)
            continue

        if f.endswith('.dpkg-new') or f.endswith('.dpkg-old') or \
           f.endswith('.dpkg-dist') or f.endswith('.rpmnew') or \
           f.endswith('.rpmsave') or f.endswith('~'):
            debug("Skipping '%s'" % (f))
            continue

	# Try to gracefully handle huge files for the user (no security
        # benefit, just usability)
        size = 0
        try:
            size = os.stat(abs)[ST_SIZE]
        except Exception:
            warn_msg = _("Skipping '%s': couldn't stat") % (f)
            warn(warn_msg)
            continue

        if size > max_size:
            warn_msg = _("Skipping '%s': too big") % (f)
            warn(warn_msg)
            continue

        if total_size + size > max_size:
            warn_msg = _("Skipping '%s': too many files read already") % (f)
            warn(warn_msg)
            continue

        total_size += size

        cdict = RawConfigParser()
        try:
            cdict.read(abs)
        except Exception:
            warn_msg = _("Skipping '%s': couldn't process") % (f)
            warn(warn_msg)
            continue

        # If multiple occurences of profile name, use the last one
        for p in cdict.sections():
            skip = False
            for key, value in cdict.items(p):
                if len(p) > 64:
                    warn_msg = _("Skipping '%s': name too long") % (p)
                    warn(warn_msg)
                    skip = True
                    break
                if len(key) > 64:
                    warn_msg = _("Skipping '%s': field too long") % (p)
                    warn(warn_msg)
                    skip = True
                    break
                if len(value) > 1024:
                    warn_msg = _("Skipping '%s': value to long for '%s'") % \
                                (p, key)
                    warn(warn_msg)
                    skip = True
                    break
            if skip:
                continue

            if profiles.has_key(p):
                warn_msg = _("Duplicate profile '%s', using last found") % (p)
                warn(warn_msg)

            pdict = {}
            for key, value in cdict.items(p):
                pdict[key] = value

            profiles[p] = pdict

    return profiles

def verify_profile(profile):
    '''Make sure profile has everything needed'''
    required_fields = ['title', 'description', 'port']

    for f in required_fields:
        if not profile.has_key(f) or not profile[f]:
            return False

    try:
        (port, proto) = ufw.util.parse_port_proto(profile['port'])
    except Exception:
        return False

    return True

