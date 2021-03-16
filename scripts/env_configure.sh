#!/bin/sh

AG_FLAGS="-q=2"

# QEMU
echo "Installing QEMU (userspace emulation)..."
sudo apt-get $AG_FLAGS install qemu-user

echo "Preparing for installing QEMU (system emulation)..."
sudo apt-get $AG_FLAGS install make
sudo apt-get $AG_FLAGS install ninja-build
echo "Installing QEMU (system emulation)..."
wget -nv https://download.qemu.org/qemu-5.2.0.tar.xz
tar -x -f qemu-5.2.0.tar.xz
cd qemu-5.2.0
./configure
make
sudo make install
cd ..

# as
echo "Installing as for ARM..."
sudo apt-get $AG_FLAGS install gcc-arm-linux-gnueabi
echo "Installing as for AVR..."
sudo apt-get $AG_FLAGS install binutils-avr

# gdb
echo "Preparing for installing GDB..."
sudo apt-get $AG_FLAGS makeinfo
sudo apt-get $AG_FLAGS install libgmp-dev
sudo apt-get $AG_FLAGS install libbfd-dev
wget -nv https://ftp.gnu.org/gnu/gdb/gdb-10.1.tar.gz
tar -x -f gdb-10.1.tar.gz
cd gdb-10.1.tar.gz

echo "Installing GDB for x86_64..."
./configure --target=x86_64-unknown-linux-gnu74
make
sudo make install
make clean
make distclean
echo "Installing GDB for ARM..."
./configure --target=arm-linux-gnueabi
make
sudo make install
make clean
make distclean
echo "Installing GDB for AVR..."
./configure --target=avr-unknown-none
make
sudo make install
make clean
make distclean
