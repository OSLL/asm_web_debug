import subprocess

class ASManager:

        # Constants:
	as_exec_path = {"x86_64" : "x86_64-linux-gnu-as",\
                        "arm"    : "arm-linux-gnueabi-as",\
                        "avr"    : "avr-as"}
	ld_exec_path = {"x86_64" : "x86_64-linux-gnu-ld",\
			"arm"    : "arm-linux-gnueabi-ld",\
			"avr"    : "avr-ld"}
	as_run_flags = {"avr" : ["-g", "-mmcu=avr6"]}
	ld_run_flags = {"avr" : ["-m", "avr6"]}


        # Static methods:

	# Description:
	# Compiles a file using assembler program with specified architecture.
	# Arguments:
	#	filename - name of source file to be compiled (.s)
	#	out_filename - name of object file to output to (.o)
	#	arch - architecture name string
	# Return values:
	#	1) [bool] if compiling was successful
<<<<<<< HEAD:src/app/core/as_manager.py
	#	2) [str] as logs (stderr)
	#	3) [str] as logs (stdout)
	def compile(filename, out_filename, arch):

		# Setting up run flags
		as_manager.compile_flags = ["-g"]
		if arch in as_manager.as_run_flags:
			as_manager.compile_flags.extend(as_manager.as_run_flags[arch])

		# Setting up executable path
		if arch in as_manager.as_exec_path:
			as_manager.exec_path = as_manager.as_exec_path[arch]
=======
	#	2) [str] as logs
	@classmethod
	def compile(cls, filename, arch):

		# Setting up run flags
		cls.run_flags = ["-g"]
		if arch in cls.arch_run_flags:
			cls.run_flags.extend(cls.arch_run_flags[arch])

		# Setting up executable path
		if arch in cls.arch_exec_path:
			cls.exec_path = cls.arch_exec_path[arch]
>>>>>>> b1c48650c7a328e0295e47e5c84098f422b2973f:src/app/core/asmanager.py
		else:
			cls.exec_path = "as" # default assemler for system

		# Remembering information about compiled file
<<<<<<< HEAD:src/app/core/as_manager.py
		as_manager.arch = arch
		as_manager.source_filename = filename
		as_manager.object_filename = out_filename

		# Forming arguments to as process
		args = [as_manager.exec_path]
		args.extend(as_manager.compile_flags)
		args.extend([as_manager.source_filename, "-o", as_manager.object_filename])
=======
		cls.arch = arch
		cls.filename = filename
		cls.output_filename = filename + ".o"

		# Forming arguments to as process
		args = [cls.exec_path]
		args.extend(cls.run_flags)
		args.extend([cls.filename, "-o", cls.output_filename])
>>>>>>> b1c48650c7a328e0295e47e5c84098f422b2973f:src/app/core/asmanager.py

		# Returning response from as
		as_resp = subprocess.run(args, capture_output = True)
		return not as_resp.returncode, as_resp.stderr, as_resp.stdout

	# Description:
	# Links an object file using linker program with specified architecture.
	# Arguments:
	#	filename - name of object file to be linked (.o)
	#	out_filename - name of executable file to output to
	#	arch - architecture name string
	# Return values:
	#	1) [bool] if linking was successful
	#	2) [str] ld logs (stderr)
	#	3) [str] ld logs (stdout)
	def link(filename, out_filename, arch):

		# Setting up run flags
		as_manager.compile_flags = []
		if arch in as_manager.ld_run_flags:
			as_manager.compile_flags.extend(as_manager.ld_run_flags[arch])

		# Setting up executable path
		if arch in as_manager.ld_exec_path:
			as_manager.exec_path = as_manager.ld_exec_path[arch]
		else:
			as_manager.exec_path = "ld" # default linker for system

		# Remembering information about compiled file
		as_manager.arch = arch
		as_manager.object_filename = filename
		as_manager.exec_filename = out_filename

		# Forming arguments to ld process
		args = [as_manager.exec_path]
		args.extend(as_manager.compile_flags)
		args.extend([filename, "-o", out_filename])

		# Returning response from ld
		ld_resp = subprocess.run(args, capture_output = True)
		return not ld_resp.returncode, ld_resp.stderr, ld_resp.stdout
