import subprocess

class as_runner:

	# Constants:
	arch_exec_path = {"x86_64" : "x86_64-linux-gnu-as",\
			  "arm"    : "arm-linux-gnueabi-as",\
			  "avr"    : "avr-as"}
	arch_run_flags = {"avr" : ["-g", "-mmcu=avr6"]}

	# Instance methods:

	# Default constructor that sets up default flags.
	def __init__(self, arch):
		self.run_flags = ["-g"]
		if arch in as_runner.arch_run_flags:
			self.run_flags.extend(as_runner.arch_run_flags[arch])

		if arch in as_runner.arch_exec_path:
			self.exec_path = as_runner.arch_exec_path[arch]
		else:
			self.exec_path = "as" # default assemler for system

	# Method that creates an as subprocess and waits for it to finish.
	# Arguments:
	#	in_path [str] - full path to input file
	#	out_path [str] - full path to output file
	def run(self, in_path, out_path):
		args = [self.exec_path]
		args.extend(self.run_flags)
		args.extend([in_path, "-o", out_path])
		return subprocess.run(args, capture_output = True)
