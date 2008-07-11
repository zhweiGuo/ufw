#!/bin/sh

#    Copyright (C) 2008 Canonical Ltd.
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
tests="installation bad good util"
CUR=`pwd`
export TESTPATH="$CUR/$testdir/testarea"
export TESTTMP="$CUR/$testdir/testarea/tmp"

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

if [ -e "/proc/sys/net/ipv6" ]; then
	tests="$tests ipv6"
fi

if [ ! -z "$1" ]; then
	tests="$1"
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
for class in $tests
do
	for d in `ls -d -1 $testdir/$class/* 2>/dev/null`
	do
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

		mkdir -p $testdir/testarea/usr/sbin $testdir/testarea/etc $testdir/testarea/tmp || exit 1

		install_dir="$CUR/$testdir/testarea"
		python ./setup.py install --home="$install_dir" > /dev/null
		if [ "$?" != "0" ]; then
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
			diffs=`diff $testdir/$class/$thistest/result $TESTTMP/result`
			if [ -z "$diffs" ]; then
				echo "    PASS"
			else
				errors=$(($errors + 1))
				echo "    FAIL:"
				echo "$diffs"
			fi
		fi
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

echo ""
echo "-------"
echo "Results"
echo "-------"
echo "Attempts:      $numtests"
echo "Skipped:       $skipped"
echo "Errors:        $errors"

if [ "$errors" != "0" ]; then
	exit 1
fi
if [ "$skipped" != "0" ]; then
	exit 2
fi

exit 0

