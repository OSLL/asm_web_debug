"""

arm-none-eabi-as -march=armv7-a -mcpu=cortex-a5 -o user.arm.obj user.arm.S 
arm-none-eabi-ld -o user.arm.temp user.arm.obj
arm-none-eabi-objcopy --only-keep-debug user.arm.temp user.arm.debug
arm-none-eabi-objcopy -O binary user.arm.temp user.arm.binonly
dd if=/dev/zero of=user.arm.bin bs=4096 count=4096
dd if=user.arm.binonly of=user.arm.bin bs=4096 conv=notrunc					


INSTALL:

arm-none-eabi-***
	sudo apt install gcc-arm-none-eabi

qemu-system-arm -cpu help
qemu-system-arm -machine help


qemu-system-arm -m 1024M -M versatilepb \
                -kernel vmlinuz-3.2.0-4-versatile -initrd initrd.gz \
                -append "root=/dev/ram" -hda armdisk.img -no-reboot

qemu-system-arm -M verdex -pflash flash -monitor null -nographic -m 289

"""


import subprocess

DIR_SRC = "user-space/src/"
DIR_OBJ = "user-space/obj/"
DIR_BIN = "user-space/bin/"
DIR_DEBUG = "user-space/debug-symbol/"


ARM_AS_PARAMS = ["arm-none-eabi-as", 
				"-march=armv7-a", 
				"-mcpu=cortex-a5"]

ARM_LD_PARAMS = ["arm-none-eabi-ld"]



def compile_arm(name):

	source_full_path  = DIR_SRC + name + ".S"
	object_full_path  = DIR_OBJ + name + ".obj"
	temp_full_path    = DIR_BIN + name + ".temp"
	debug_full_path   = DIR_DEBUG + name + ".debug"
	binonly_full_path = DIR_BIN + name + ".binary"
	bin_full_path     = DIR_BIN + name + ".bin"


	status = subprocess.call(ARM_AS_PARAMS + [
										"-o", object_full_path,
										source_full_path
									])
	if ( status != 0 ):
		print ("compile error")
		exit(1)


	status = subprocess.call(ARM_LD_PARAMS + [
										"-o", temp_full_path,
										object_full_path
									])
	if ( status != 0 ):
		subprocess.call(["rm", object_full_path])
		print ("linker error")
		exit(1)


	status = subprocess.call(["arm-none-eabi-objcopy", 
								"--only-keep-debug", 
								temp_full_path, 
								debug_full_path])
	if ( status != 0 ):
		subprocess.call(["rm", object_full_path,
							   temp_full_path])
		print ("arm-none-eabi-objcopy error")
		exit(1)


	status = subprocess.call(["arm-none-eabi-objcopy", 
								"-O", "binary", 
								temp_full_path,
								binonly_full_path])
	if ( status != 0 ):
		subprocess.call(["rm", object_full_path,
							   temp_full_path,
							   debug_full_path])
		print ("arm-none-eabi-objcopy error")
		exit(1)


	subprocess.call(["dd",
								"if=" + "/dev/zero",
								"of=" + bin_full_path,
								"bs=4096", "count=4096"])


	subprocess.call(["dd",
								"if=" + binonly_full_path,
								"of=" + bin_full_path,
								"bs=4096", "conv=notrunc"])

	

	status = subprocess.call(["rm", temp_full_path])
	status = subprocess.call(["rm", binonly_full_path])



compile_arm("user.arm")

