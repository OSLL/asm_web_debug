import subprocess
from flask import current_app

class CompileError(Exception):
	pass

"""
x86
	qemu-system-x86_64 -kernel a.out -m 10M  -no-reboot 
	ld -melf_i386 -T linker.ld  main.S.o


	#arm-linux-gnueabi-as
"""

class ASManager:

        # Constants:
	arch_exec_path = {"x86" : "x86_64-linux-gnu-as",\
                          "arm"    : "arm-none-eabi-as",\
                          "avr"    : "avr-as"}

	arch_run_flags = {"avr" : ["-g", "-mmcu=avr6"],\
					  "x86" : ["-32"],\
					  "arm" : ["-march=armv7-a", "-mcpu=cortex-a5"]}

	arch_link_flags = {"avr" : ["avr-ld", "-m avr1"],\
					  "x86" : ["x86_64-linux-gnu-ld", "-melf_i386"],\
					  "arm" : ["arm-none-eabi-ld"]}

        # Static methods:

	# Description:
	# Compiles a file using assembler program with specified architecture.
	# Arguments:
	#	filename - name of source file to be compiled (.s)
	#	arch - architecture name string
	#	dependence - depend files dir path
	# Return values:
	#	1) [bool] if compiling was successful
	#	2) [str] as logs
	@classmethod
	def compile(cls, filename, arch, dependence):

		if not arch in current_app.config["ARCHS"]:
			raise CompileError('unknown arch')

		# Setting up run flags
		cls.run_flags = ["-g"]
		if arch in cls.arch_run_flags:
			cls.run_flags.extend(cls.arch_run_flags[arch])

		# Setting up executable path
		if arch in cls.arch_exec_path:
			cls.exec_path = cls.arch_exec_path[arch]
		else:
			cls.exec_path = "as" # default assemler for system

		# Remembering information about compiled file
		cls.arch = arch
		cls.filename = filename
		cls.object_filename = filename + ".o"
		cls.binary_filename = filename + ".bin"
		cls.debug_filename  = filename + ".debug"

		# Forming arguments to as process
		args = [cls.exec_path]
		args.extend(cls.run_flags)
		args.extend([cls.filename, "-o", cls.object_filename])

		# Returning response from as
		as_resp = subprocess.run(args, capture_output = True)
		if as_resp.returncode != 0:
			return not as_resp.returncode, as_resp.stderr, as_resp.stdout


			
		
		args_ld = []
		args_ld.extend(cls.arch_link_flags[arch])

		if arch == "x86":
			args_ld.extend(["-T", dependence + "linker.ld",\
						"-o", cls.binary_filename, cls.object_filename])

		elif arch == "arm":
			args_ld.extend(["-o", cls.binary_filename, cls.object_filename])

		elif arch == "avr":
			args_ld.extend(["-o", cls.binary_filename, cls.object_filename])
			pass
		else:
			raise CompileError('linker for {0} arch not found'.format(arch))
			
		as_resp = subprocess.run(args_ld, capture_output = True)

		return not as_resp.returncode, as_resp.stderr, as_resp.stdout
