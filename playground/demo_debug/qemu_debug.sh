#!/bin/sh

PROG_DIR="demos"
USAGE_MSG="Usage: $0 <target architecture> <executable in \"./$PROG_DIR\" without \".out\">"

if [ "$1" = "" ]; then
	echo $USAGE_MSG
	exit
fi
if [ "$2" = "" ]; then
	echo $USAGE_MSG
	exit
fi

gdb_binaries/gdb_$1 $PROG_DIR/$2.$1.out -q -ex "target extended-remote localhost:1234"
