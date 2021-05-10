import subprocess
import os
from flask import current_app

class CompileError(Exception):
	pass


class ASManager:

        # Constants:
	arch_exec_path = {"x86_64" : "gcc"}
	
						  #,
                          #"arm"    : "arm-none-eabi-as",
                          #"avr"    : "avr-as"}


	arch_build_flags = {"x86_64" : ["-no-pie", "-nodefaultlibs", "-nostartfiles", "-g"],\
					  "avr" : ["-g", "-mmcu=avr6"],\
					  "arm" : ["-march=armv7-a", "-mcpu=cortex-a5"]}

	arch_link_flags = {"avr" : ["avr-ld", "-m avr1"],\
					  "x86_64" : ["x86_64-linux-gnu-ld", "-melf_i386"],\
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
	def compile(cls, filename, arch):
		# Remembering information about compiled file
		cls.arch = arch
		cls.filename = filename
		cls.binary_filename = filename + ".bin"
		cls.build_flags = []
		cls.exec_path = None


		if not arch in current_app.config["ARCHS"] or not arch in cls.arch_exec_path:
			raise CompileError('Compile error: unknown arch')

		if not os.path.isfile(filename):
			raise FileNotFoundError('Compile error: file \'{0}\' not found'.format(filename))


		# Setting up run flags
		if arch in cls.arch_build_flags:
			cls.build_flags.extend(cls.arch_build_flags[arch])

		# Setting up executable path
		if arch in cls.arch_exec_path:
			cls.exec_path = cls.arch_exec_path[arch]
		else:
			raise CompileError('unknown arch')


		# Forming arguments to as process
		args = [cls.exec_path]
		args.extend(cls.build_flags)
		args.extend([cls.filename, "-o", cls.binary_filename])

		# Returning response from as
		as_resp = subprocess.run(args, capture_output = True)

		return not as_resp.returncode, as_resp.stderr, as_resp.stdout