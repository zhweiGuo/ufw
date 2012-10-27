#!/usr/bin/python
#
# find_tests() and main() based on Lib/test/regrtest.py from Python 3.1
# Copyright (c) 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010
# Python Software Foundation; All Rights Reserved

# runner.py: test runner for unit tests
#

from __future__ import print_function


import os
import sys

# Based on 
def find_tests(testdir=None):
    '''Find tests'''
    if not testdir:
        if __name__ == '__main__':
            fn = sys.argv[0]
        else:
            print("TODO: find_tests() when imported")
            sys.exit(1)

        testdir = os.path.dirname(fn)

    names = os.listdir(testdir)
    tests = []
    for name in names:
        if name[:5] == "test_" and name[-3:] == ".py":
            tests.append(name[:-3])
    tests.sort()
    return tests

def runtest(test):
    '''Run test'''
    pkg =  __import__("tests.unit." + test, globals(), locals(), [])
    unit_pkg = getattr(pkg, "unit")
    mod = getattr(unit_pkg, test)
    print(test)
    mod.test_main()


if __name__ == '__main__':
    # Replace runner.py's directory from the search path, and add our own
    # so we can properly namespace our modules
    d = os.path.abspath(os.path.normpath(os.path.dirname(sys.argv[0])))
    testdir = os.path.dirname(d)
    testdir = os.path.dirname(os.path.dirname(d))
    i = len(sys.path)
    while i >= 0:
        i -= 1
        if os.path.abspath(os.path.normpath(sys.path[i])) == d:
            sys.path[i] = testdir

    print("DEBUG: sys.path=%s" % sys.path)
    tests = find_tests()
    print("DEBUG: test=%s" % str(tests))

    # Import this here, so we are guaranteed to get ours from topdir
    from tests.unit.support import TestFailed

    #if trace:
    #    print("TODO: trace")
    #    sys.exit(1)

    passed = []
    failed = []
    skipped = []
    for test in tests:
        try:
            runtest(test)
            passed.append(test)
        except KeyboardInterrupt: # kill this test, but still do others
            print("")
            break
        except TestFailed as e:
            failed.append(test)
        except:
            raise

        # cleanup
        for m in sys.modules.keys():
            if m.startswith("tests.unit.") and m != "tests.unit.support":
                try:
                    del sys.modules[m]
                except KeyError:
                    pass

    print("")
    print("------------------")
    print("Unit tests summary")
    print("------------------")
    print("Total=%d (Passed=%d, Failed=%d)" % (len(passed) + len(failed),
                                               len(passed),
                                               len(failed)))
    if len(failed) > 0:
        sys.exit(1)
