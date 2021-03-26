import asyncio
from demo_debug.py_demo import socket_util

class qemu_runner:

	# Constants:
	# {0} is debug port
	arch_run_flags = {"avr" : "-machine mega -display none -S -gdb tcp::{0}"}

	# Instance methods:

	# Default constructor that sets up class fields.
	def __init__(self, arch):
		self.arch = arch
		self.dbg_port = None

		self.run_flags = "-g {0}"
		if arch in qemu_runner.arch_run_flags:
			self.run_flags = qemu_runner.arch_run_flags[arch] # they're replaced, not extended


	# Private method to be run via asyncio.run() that creates a subprocess.
	async def __run_func(self, exec_path):
		if self.arch == "avr":
			qemu_cmd = "qemu-system-avr {0} -bios {1}".format(
						self.run_flags.format(self.dbg_port),
						exec_path)
		else:
			qemu_cmd = "qemu-{0} {1} {2}".format(
						self.arch,
						self.run_flags.format(self.dbg_port),
						exec_path)

		self.proc = await asyncio.create_subprocess_shell(qemu_cmd,
							None, asyncio.subprocess.DEVNULL, asyncio.subprocess.DEVNULL)

	# Method that creates a QEMU subprocess that runs the specified executable.
	# Arguments:
	#	exec_path [str] - full path to executable file (can be local)
	def run(self, exec_path):
		self.cur_exec = exec_path
		if not self.dbg_port:
			self.dbg_port = socket_util.probe_for_port("localhost")
		if self.dbg_port == None:
				return False

		asyncio.run(self.__run_func(exec_path))

