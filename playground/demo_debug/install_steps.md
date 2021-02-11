# Шаги установки демонстрационной программы
## Установка эмуляции пользовательского режима (userspace)
```
sudo apt install qemu-user
```

## Установка и сборка QEMU
#### Исходный код QEMU
```
https://download.qemu.org/qemu-5.2.0.tar.xz
```
#### Утилиты для сборки
```
sudo apt-get install make
sudo apt-get install ninja-build
```
#### Сборка исходного кода
```
./configure
make
make install
```

## Установка ассемблера
#### ARM
```
sudo apt install gcc-arm-linux-gnueabi
```
#### AVR
```
sudo apt install binutils-avr
```
## Установка и сборка GDB
Для простоты установки и использования здесь приведены шаги для сборки отдельных исполняемых файлов, но не установки их на конечную операционную систему. Вместо этого полученные исполняемые файлы должны быть перемещены в директорию демонстрационной программы `gdb_binaries/`.
```
mkdir gdb_binaries
```
#### Утилиты для сборки
```
sudo apt-get install make
sudo apt-get install makeinfo
```
#### Зависимости GDB
```
sudo apt-get install libgmp-dev
sudo apt-get install libbfd-dev
```
#### Исходный код GDB
```
ftp://sourceware.org/pub/gdb/snapshots/branch/
```
#### Сборка исходного кода
После каждой сборки нужно выполнить следующие команды для очистки файлов конфигурации:
```
make clean
make distclean
```
##### Сборка для x86_64
```
./configure --target=x86_64-unknown-linux-gnu74
make
mv ./gdb/gdb ../gdb_binaries/gdb_x86_64
```
##### Сборка для ARM
```
./configure --target=arm-linux-gnueabi
make
mv ./gdb/gdb ../gdb_binaries/gdb_arm
```
##### Сборка для AVR
```
./configure --target=avr-unknown-none
make
mv ./gdb/gdb ../gdb_binaries/gdb_avr
```

# Шаги установки для запуска модуля на Python
## Зависимости
```
pip3 install pygdbmi
```

# Использование демонстрационной программы
Запуск производится при помощи bash-скрипта `./qemu_run.sh` со следующими аргументами:
```
./qemu_run.sh <целевая архитектура> <исполняемый файл в ./demos/ без расширения ".out"> [режим запуска: обычный (normal) / отладочный (debug)]
```
При запуске в отладочном режиме эмулятор QEMU ждёт подключения через TCP-порт отладчика GDB. Запустить GDB можно при помощи скрипта `./qemu_debug.sh`:
```
./qemu_debug.sh <целевая архитектура> <исполняемый файл в ./demos/ без расширения ".out">
```
