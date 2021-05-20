"""
	qemu-system-x86_64 -kernel a.out -m 10M  -no-reboot 
	ld -melf_i386 -T linker.ld  main.S.o



	ld -Ttext=0x101000 -Tdata=0x100000 -melf_i386 mboot.o -o kernel.elf

	qemu-system-x86_64 -kernel user-space/bin/user-n001 -m 10M -s -S
	qemu-system-x86_64 -kernel a.out -m 10M  -no-reboot 
	ld -melf_i386 -T linker.ld  main.S.o

-qemu-system-i386 -fda disk.img

Подключение отладчика: (запуск необходимо произвести в каталоге system-qemu/)

gdb

target remote localhost:1234

symbol-file user-space/debug-symbol/user-n001.debug    

break EntryPoint 			

continue		

Сейчас мы находимся в исполняемом коде					

////////////////
x/10i $eip
stepi
nexti
////////////////



status = subprocess.call(["qemu-system-x86_64", "-kernel", "bin/" + uc_file, "-m 1G"])

if ( status != 0 ):
	print ("start error")
	exit()
"""



import subprocess

DIR_SRC = "user-space/src/"
DIR_OBJ = "user-space/obj/"
DIR_BIN = "user-space/bin/"
DIR_DEBUG = "user-space/debug-symbol/"


x86_AS_PARAMS = ["as", 
				"-32", "-g"]

x86_LD_PARAMS = ["ld", 
				"-melf_i386", 
				"-T", "linker.ld"]



def compile_x86(name):

	source_full_path  = DIR_SRC + name + ".S"
	object_full_path  = DIR_OBJ + name + ".obj"
	debug_full_path   = DIR_DEBUG + name + ".debug"
	bin_full_path     = DIR_BIN + name + ".bin"

	status = subprocess.call(x86_AS_PARAMS + [
									"-o", object_full_path, 
									source_full_path])
	if ( status != 0 ):
		print ("compile error")
		exit(1)


	status = subprocess.call(x86_LD_PARAMS + [
									"-o", bin_full_path, 
									object_full_path, 
									"user-space/loader.obj"])
	if ( status != 0 ):
		subprocess.call(["rm", object_full_path])
		print ("linker error")
		exit(2)

	status = subprocess.call(["objcopy", "--only-keep-debug", 
									bin_full_path, 
									debug_full_path])
	if ( status != 0 ):
		subprocess.call(["rm", object_full_path, bin_full_path])
		print ("debug-info error")
		exit(3)
   

compile_x86("user.x86")