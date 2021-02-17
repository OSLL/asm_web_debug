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
status = subprocess.call(["qemu-system-x86_64", "-kernel", "bin/" + uc_file, "-m 1G"])

if ( status != 0 ):
	print ("start error")
	exit()
"""