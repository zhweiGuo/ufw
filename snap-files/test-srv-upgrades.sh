#!/bin/sh
set -e

export SNAP_SKIP_INIT="yes"

testdir="$(mktemp -d)"
#shellcheck disable=SC2064
trap "rm -rf '$testdir'" EXIT HUP INT QUIT TERM


curdir="$(pwd)"
cd "$testdir"
tar -zxvf "$curdir/test-srv-upgrades-data.tar.gz"

echo "== Clean out everything"
rm -rf "$testdir"/var/snap/ufw/*/* "$testdir"/var/snap/ufw/*/.[eru]* "$testdir"/var/snap/ufw/8*

echo
echo "== Run srv on 23 for the first time"
SNAP="$testdir"/snap/ufw/23 SNAP_DATA="$testdir"/var/snap/ufw/23 SNAP_REVISION=23 "$curdir"/bin/srv

echo
echo "== Convert 23 back to rules.orig"
mkdir "$testdir"/var/snap/ufw/23/.rules.orig
cp "$testdir"/snap/ufw/23/etc/ufw/*.rules "$testdir"/var/snap/ufw/23/.rules.orig
rm -f "$testdir"/var/snap/ufw/23/.rules.orig/user*rules
rm -rf "$testdir"/var/snap/ufw/23/.etc.last

echo
echo "== Simulate upgrade from 23 to 85"
cp -a "$testdir"/var/snap/ufw/23 "$testdir"/var/snap/ufw/85

echo
echo "== Run srv on 85"
SNAP="$testdir"/snap/ufw/85 SNAP_DATA="$testdir"/var/snap/ufw/85 SNAP_REVISION=85 "$curdir"/bin/srv

echo
echo "== Simulate upgrade from 85 to 86"
cp -a "$testdir"/var/snap/ufw/85 "$testdir"/var/snap/ufw/86

echo
echo "== Run srv on 86"
SNAP="$testdir"/snap/ufw/86 SNAP_DATA="$testdir"/var/snap/ufw/86 SNAP_REVISION=86 "$curdir"/bin/srv
