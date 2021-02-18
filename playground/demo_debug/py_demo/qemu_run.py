if __name__ != "__main__":

	import asyncio
	import socket_util

	class qemu_runner:

		# Static methods:

		# Method that tries to find a class that matches given architecture name,
		# and create it's instance with provided arguments.
		# Initializes and returns qemu_runner object if the class wasn't found.
		# Arguments:
		#	caller_globals - globals() dictionary of module that calls this function.
		#	arch - target architecture string.
		#	*init_args - arguments for target runner class, if any.
		def get_by_arch(caller_globals, arch, *init_args):
			try:
				return caller_globals["qemu_runner_" + arch](*init_args)
			except KeyError:
				qmrun = qemu_runner()
				qmrun.arch = arch
				return qmrun


		# Instance methods:

		# Default constructor that sets flags for QEMU, but doesn't specify architecture.
		# Arguments:
		#	arch - target architecture.
		def __init__(self):
			self.arch = None
			self.run_flags = ""


		# Private method to be run via asyncio.run() that creates a subprocess.
		async def __run_func(self, exec_path):
			qemu_cmd = "qemu-{0} {1} {2}".format(
						self.arch, self.run_flags, exec_path)
			self.proc = await asyncio.create_subprocess_shell(qemu_cmd,
								None, asyncio.subprocess.DEVNULL, asyncio.subprocess.DEVNULL)

		# Method that creates a QEMU subprocess that runs the specified executable.
		# Arguments:
		#	exec_path [str] - full path to executable file (can be local)
		def run(self, exec_path):
			self.cur_exec = exec_path
			self.dbg_port = socket_util.probe_for_port("localhost")
			if self.dbg_port == None:
				return False
			self.run_flags += "-g " + str(self.dbg_port)
			asyncio.run(self.__run_func(exec_path))

