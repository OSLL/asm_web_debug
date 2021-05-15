



"""

AVR

avr-as -mmcu=atmega32u4 -g user-n002.avr.asm 
avr-ld -m avr1 -o res a.out

Continuous non interrupted execution:

qemu-system-avr -machine mega2560 -bios demo.elf

Continuous non interrupted execution with serial output into telnet window:

qemu-system-avr -M mega2560 -bios demo.elf -nographic 
                -serial tcp::5678,server=on,wait=off

and then in another shell:

telnet localhost 5678

Debugging with GDB debugger:

qemu-system-avr -machine mega2560 -bios demo.elf -s -S



"""