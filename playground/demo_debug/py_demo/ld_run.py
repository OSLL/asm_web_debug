if __name__ != "__main__":

	import subprocess

	class ld_runner:

		# Static methods:

		# Method that tries to find a class that matches given architecture name
		# and create an instance of it with provided arguments.
		# Initializes and returns ld_runner instance if requested class wasn't found.
		# Arguments:
		#	caller_globals - globals() of module that calls this function.
		#	arch - target architecture string.
		#	*init_args - arguments for creating an instance of target class, if any.
		def get_by_arch(caller_globals, arch, *init_args):
			try:
				return caller_globals["ld_runner_" + arch](*init_args)
			except KeyError:
				ldrun = ld_runner()
				return lrun


		# Instance methods:

		# Default constructor that sets up default flags.
		def __init__(self):
			self.run_flags = []
			self.exec_path = "ld" # default linker for system

		# Method that creates an ld subprocess and waits for it to finish.
		# Arguments:
		#	in_path [str] - full path to input file
		#	out_path [str] - full path to output file
		def run(self, in_path, out_path):
			args = [self.exec_path]
			args.extend(self.run_flags)
			args.extend([in_path, "-o", out_path])
			return subprocess.run(args, capture_output = True)
