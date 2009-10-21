#!/bin/sh

#    Copyright 2008-2009 Canonical Ltd.
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

testdir="tests"
tests="installation bad bugs good util"

ipt_major=`iptables --version | sed 's/.* v//' | cut -d '.' -f 1 | sed 's/\([0-9]\+\).*/\\1/'`
ipt_minor=`iptables --version | sed 's/.* v//' | cut -d '.' -f 2 | sed 's/\([0-9]\+\).*/\\1/'`
ipt_micro=`iptables --version | sed 's/.* v//' | cut -d '.' -f 3 | sed 's/\([0-9]\+\).*/\\1/'`

get_result_path() {
    d="$1"
    f="$d/result"

    f_micro="$f.$ipt_major.$ipt_minor.$ipt_micro"
    f_minor="$f.$ipt_major.$ipt_minor"

    if [ -f "$f.$ipt_major.$ipt_minor.$ipt_micro" ]; then
        f="$f_micro"
    elif [ -f "$f.$ipt_major.$ipt_minor" ]; then
        f="$f_minor"
    fi

    echo "$f"
}

CUR=`pwd`
export TESTPATH="$CUR/$testdir/testarea"
export TESTTMP="$CUR/$testdir/testarea/tmp"
export TESTSTATE="$TESTPATH/lib/ufw"

STOPONFAIL="no"
STOPONSKIP="no"
if [ "$1" = "-s" ]; then
    shift
    STOPONFAIL="yes"
elif [ "$1" = "-S" ]; then
    shift
    STOPONFAIL="yes"
    STOPONSKIP="yes"
fi

interpreter=""
if [ "$1" = "-i" ]; then
    shift
    if [ -z "$1" ]; then
        echo "Specified '-i' without an interpreter. Aborting" &>2
        exit
    fi
    interpreter="$1"
    shift
fi
if [ -z "$interpreter" ]; then
    for exe in python python2.6 python2.5; do
        if which $exe >/dev/null 2>&1; then
            interpreter="$exe"
            break
        fi
    done
fi
# export the interpreter so the tests can use it too
export interpreter="$interpreter"

echo "Interpreter: $interpreter"
echo ""

if [ -e "/proc/sys/net/ipv6" ]; then
    tests="$tests ipv6"
fi

subclass=""
if [ ! -z "$1" ]; then
    tmp="$1"
    if echo "$tmp" | egrep -q '/' ; then
        subclass=`basename $tmp`
        tests=`dirname $tmp`
    else
        tests="$tmp"
    fi
fi

if [ ! -d "$testdir" ]; then
    echo "Couldn't find '$testdir' directory"
    exit 1
fi

if [ ! -e "./setup.py" ]; then
    echo "Couldn't find setup.py"
    exit 1
fi

skipped=0
errors=0
numtests=0

statsdir=`mktemp -d`
trap "rm -rf $statsdir" EXIT HUP INT QUIT TERM
export statsdir
echo "0" > $statsdir/individual

for class in $tests
do
    for d in `ls -d -1 $testdir/$class/* 2>/dev/null`
    do
        if [ ! -z "$subclass" ]; then
            if [ "$d" != "$testdir/$class/$subclass" ]; then
                continue
            fi
        fi

        if [ $skipped -gt 0 ]; then
            if [ "$STOPONSKIP" = "yes" ]; then
                echo ""
                echo "STOPONSKIP set, exiting on skip"
                exit 1
            fi
        fi
        thistest=`basename $d`
        echo ""
        echo "Performing tests '$class/$thistest'"

        if [ ! -x "$CUR/$testdir/$class/$thistest/runtest.sh" ]; then
            skipped=$(($skipped + 1))
            echo "    WARNING: couldn't find '$CUR/$testdir/$class/$thistest/runtest.sh' (skipping)"
            continue
        fi

        echo "- installing"
        if [ -d "$testdir/testarea" ]; then
            rm -rf $testdir/testarea
        fi
        tmpdir=`mktemp -d`
        mv "$tmpdir" "$testdir/testarea"

        mkdir -p $testdir/testarea/usr/sbin $testdir/testarea/etc $testdir/testarea/tmp || exit 1

        install_dir="$CUR/$testdir/testarea"
        setup_output=`$interpreter ./setup.py install --home="$install_dir" 2>&1`
        if [ "$?" != "0" ]; then
            echo "$setup_output"
            exit 1
        fi

        # this is to allow root to run the tests without error.  I don't
        # like building things as root, but some people do...
        sed -i 's/self.do_checks = True/self.do_checks = False/' $testdir/testarea/lib/python/ufw/backend.py

        cp -rL $testdir/$class/$thistest/orig/* $testdir/testarea/etc || exit 1
        cp -f $testdir/$class/$thistest/runtest.sh $testdir/testarea || exit 1

        echo "- result: "
        numtests=$(($numtests + 1))
        # now run the test
        PYTHONPATH="$PYTHONPATH:$install_dir/lib/python" $CUR/$testdir/testarea/runtest.sh
        if [ "$?" != "0" ];then
            echo "    ** FAIL **"
            errors=$(($errors + 1))
        else
            if [ ! -f "$TESTTMP/result" ]; then
                skipped=$(($skipped + 1))
                echo "    WARNING: couldn't find '$TESTTMP/result' (skipping)"
                continue
            else
                # fix discrepencies between python versions
                sed -i 's/^usage:/Usage:/' $TESTTMP/result
                sed -i 's/^options:/Options:/' $TESTTMP/result
            fi
            if [ ! -f "$testdir/$class/$thistest/result" ]; then
                skipped=$(($skipped + 1))
                echo "    WARNING: couldn't find '$testdir/$class/$thistest/result' (skipping)"
                continue
            fi

            result_file=`get_result_path $testdir/$class/$thistest`
            diffs=`diff -w $result_file $TESTTMP/result`
            if [ -z "$diffs" ]; then
                echo "    PASS"
            else
                errors=$(($errors + 1))
                echo "    FAIL:"
                echo "$diffs"
            fi
        fi
        chmod 755 "$testdir/testarea"
        if [ $errors -gt 0 ]; then
            if [ "$STOPONFAIL" = "yes" ]; then
                echo ""
                echo "FAILED $class/$thistest -- result found in $TESTTMP/result"
                exit 1
            fi
        fi
    done
done

if [ -d "$testdir/testarea" ]; then
    rm -rf $testdir/testarea
fi

individual=$(cat $statsdir/individual)

echo ""
echo "-------"
echo "Results"
echo "-------"
echo "Attempted:           $numtests ($individual individual tests)"
echo "Skipped:             $skipped"
echo "Errors:              $errors"

if [ "$errors" != "0" ]; then
    exit 1
fi

# cleanup
rm -rf $statsdir

if [ "$skipped" != "0" ]; then
    exit 2
fi

exit 0

