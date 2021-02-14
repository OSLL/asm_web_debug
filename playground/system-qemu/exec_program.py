import subprocess

uc_file = "user-n001"

status = subprocess.call(["as", "-32", "-g", "-o", "obj/" + uc_file, "user-src/" + uc_file + ".asm"])

if ( status != 0 ):
	print ("compile error")
	exit()

status = subprocess.call(["ld", "-melf_i386", "-T", "linker.ld", "-o", "bin/" + uc_file, "obj/" + uc_file, "obj/loader.obj"])

if ( status != 0 ):
	print ("link error")
	exit()

status = subprocess.call(["ld", "-melf_i386", "-T", "linker.ld", "-o", "bin/" + uc_file, "obj/" + uc_file, "obj/loader.obj"])

if ( status != 0 ):
	print ("link error")
	exit()

status = subprocess.call(["qemu-system-x86_64", "-kernel", "bin/" + uc_file, "-m 1G"])

if ( status != 0 ):
	print ("start error")
	exit()
# -boot d -cdrom uapp.iso -m 1G