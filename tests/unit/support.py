#
# Copyright 2012 Canonical Ltd.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3,
# as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# run_unittest() inspired by Lib/test/support.py from Python 3.1
# Copyright (c) 2001-2010 Python Software Foundation; All Rights Reserved

import unittest
import os
import sys

class Error(Exception):
    '''Error'''

class TestFailed(Error):
    '''Test failed'''

def skipped(cls, s):
    '''Test skipped'''
    # TODO: fix newline
    # TODO: somehow flag and count this as skipped
    print("skipped: %s" % s)
    return False

def recursive_rm(dirPath, contents_only=False):
    '''recursively remove directory'''
    names = os.listdir(dirPath)
    for name in names:
        path = os.path.join(dirPath, name)
        if os.path.islink(path) or not os.path.isdir(path):
            os.unlink(path)
        else:
            recursive_rm(path)
    if contents_only == False:
        os.rmdir(dirPath)

def run_unittest(*classes):
    '''Run tests from classes'''
    suite = unittest.TestSuite()
    for cls in classes:
        suite.addTest(unittest.makeSuite(cls))

    runner = unittest.TextTestRunner(sys.stdout, verbosity=2)
    result = runner.run(suite)
    if not result.wasSuccessful():
        if len(result.errors) == 1 and not result.failures:
            err = result.errors[0][1]
        elif len(result.failures) == 1 and not result.errors:
            err = result.failures[0][1]
        else:
            err = "multiple errors occurred"
        raise TestFailed(err)

