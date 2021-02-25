import subprocess

uc_file = "user-n001"

status = subprocess.call(["as", "-32", "-g", "-o", "user-space/obj/" + uc_file, "user-space/src/" + uc_file + ".asm"])

if ( status != 0 ):
	print ("compile error")
	exit()

status = subprocess.call(["ld", "-melf_i386", "-T", "linker.ld", "-o", "user-space/bin/" + uc_file, "user-space/obj/" + uc_file, "user-space/loader.obj"])

if ( status != 0 ):
	print ("linker error")
	exit()

status = subprocess.call(["objcopy", "--only-keep-debug", "user-space/bin/" + uc_file, "user-space/debug-symbol/" + uc_file + ".debug"])

if ( status != 0 ):
	print ("debug-info error")
	exit()
   


"""

AVR

avr-as -mmcu=atmega32u4 -g user-n002.avr.asm 
avr-ld -m avr1 -o res a.out

ARM

arm-as -mcpu=arm926ej-s -g -o user-n003.arm.obj user-n003.arm.asm


status = subprocess.call(["qemu-system-x86_64", "-kernel", "bin/" + uc_file, "-m 1G"])

if ( status != 0 ):
	print ("start error")
	exit()
"""