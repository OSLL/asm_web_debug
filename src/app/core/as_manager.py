import subprocess

class as_manager:

        # Constants:
	arch_exec_path = {"x86_64" : "x86_64-linux-gnu-as",\
                          "arm"    : "arm-linux-gnueabi-as",\
                          "avr"    : "avr-as"}
	arch_run_flags = {"avr" : ["-g", "-mmcu=avr6"]}

        # Static methods:

	# Description:
	# Compiles a file using assembler program with specified architecture.
	# Arguments:
	#	filename - name of source file to be compiled (.s)
	#	arch - architecture name string
	# Return values:
	#	1) [bool] if compiling was successful
	#	2) [str] as logs
	def compile(filename, arch):

		# Setting up run flags
		as_manager.run_flags = ["-g"]
		if arch in as_manager.arch_run_flags:
			as_manager.run_flags.extend(as_manager.arch_run_flags[arch])

		# Setting up executable path
		if arch in as_manager.arch_exec_path:
			as_manager.exec_path = as_manager.arch_exec_path[arch]
		else:
			as_manager.exec_path = "as" # default assemler for system

		# Remembering information about compiled file
		as_manager.arch = arch
		as_manager.filename = filename
		as_manager.output_filename = filename + ".o"

		# Forming arguments to as process
		args = [as_manager.exec_path]
		args.extend(as_manager.run_flags)
		args.extend([as_manager.filename, "-o", as_manager.output_filename])

		# Returning response from as
		as_resp = subprocess.run(args, capture_output = True)
		return not as_resp.returncode, as_resp.stderr, as_resp.stdout
