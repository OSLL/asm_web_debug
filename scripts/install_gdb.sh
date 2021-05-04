#!/bin/sh

set -e

apt install -y wget libgmp-dev libbfd-dev 


mkdir gdb_binaries

wget -nv https://ftp.gnu.org/gnu/gdb/gdb-10.1.tar.gz
tar -x -f gdb-10.1.tar.gz
cd gdb-10.1

echo "Installing GDB for x86_64..."
./configure --target=x86_64-unknown-linux-gnu74
make
mv ./gdb/gdb ../gdb_binaries/gdb_x86_64
make clean
make distclean

echo "Installing GDB for ARM..."
./configure --target=arm-linux-gnueabi
make
mv ./gdb/gdb ../gdb_binaries/gdb_arm
make clean
make distclean

echo "Installing GDB for AVR..."
./configure --target=avr-unknown-none
make
mv ./gdb/gdb ../gdb_binaries/gdb_avr
make clean
make distclean

cd ..
rm -rf gdb-10.1
rm gdb-10.1.tar.gz
