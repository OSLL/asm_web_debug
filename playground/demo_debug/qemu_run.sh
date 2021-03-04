#!/bin/sh

PROG_DIR="demos"
USAGE_MSG="Usage: $0 <target architecture> <executable in \"./$PROG_DIR\" without \".out\"> [mode: <normal>/debug]"

AVR_FLAGS="-machine mega -display none"

if [ "$1" = "" ]; then
	echo $USAGE_MSG
	exit
fi
if [ "$2" = "" ]; then
	echo $USAGE_MSG
	exit
fi

FLAGS=""
if [ "$3" = "debug" ]; then
	if [ "$1" = "avr" ]; then
		FLAGS="$FLAGS -s -S"
	else
		FLAGS="$FLAGS -g 1234"
	fi
fi

if [ "$1" = "avr" ]; then
	qemu-system-avr $AVR_FLAGS $FLAGS -bios $PROG_DIR/$2.$1.out
else
	qemu-$1 $FLAGS $PROG_DIR/$2.$1.out
fi
