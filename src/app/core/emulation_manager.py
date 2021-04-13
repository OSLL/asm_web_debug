import subprocess
import asyncio
from app.core.utils import socket_util

# Class that represents a running emulated process.
class EmulationInstance:

	# Instance fields:
	# arch - architecture of target executable file
	# exec_fname - name of executable file being run
	# debug_port - port used for debugging over TCP connection
	# run_args - arguments that were used to emulate the process
	# code_id - id of source code

	# proc_res - result of running an emulator process created by asyncio.create_subprocess_shell()
	# debug_ctrl - debug controller process attached to emulated one.

	def __init__(self, arch, exec_fname, debug_port, run_args, code_id):
		self.arch = arch
		self.exec_fname = exec_fname
		self.debug_port = debug_port
		self.run_args = run_args
		self.code_id = code_id

class EmulationManager:

	# Constants:

	# Format: {0} - architecture, {1} - run flags, {2} - path to executable
	arch_run_cmds =  {
				"default": "qemu-{0} {1} {2}",
				"avr"	 : "qemu-system-avr {1} -bios {2}"
			 }
	# Format: {0} - debug port
	arch_run_flags = {
				"default" : "-g {0}",
				"avr" 	  : "-machine mega -display none -S -gdb tcp::{0}"
			 }

	# Static fields:

	# Dictionary of emulation instances, should only contain pairs in form of
	# {uuid [int] : [EmulationInstance]}
	emulation_instances = {}


	# Static methods:

	# Description:
	# Creates a QEMU subprocess with specified architecture that runs specified executable.
	# Arguments:
	#	filename - full path to executable file
	#	arch - architecture of executable file
	#	code_id - id of source file
	# Return values:
	#	[EmulationInstance] - class that describes currently running emulated process,
	#	or None if it wasn't created (couldn't find a debug port)
	def run_exec(filename, arch, code_id):
		if arch in EmulationManager.arch_run_cmds:
			ecmd = EmulationManager.arch_run_cmds[arch]
		else:
			ecmd = EmulationManager.arch_run_cmds["default"]

		if arch in EmulationManager.arch_run_flags:
			eflags = EmulationManager.arch_run_flags[arch]
		else:
			eflags = EmulationManager.arch_run_flags["default"]

		debug_port = socket_util.probe_for_port("localhost")
		if debug_port == None:
			return None

		eflags = eflags.format(debug_port)
		ecmd = ecmd.format(arch, eflags, filename)

		run_inst = EmulationInstance(arch, filename, debug_port, ecmd, code_id)
		EmulationManager.emulation_instances[code_id] = run_inst

		asyncio.run(EmulationManager.__run_func(run_inst))

		return run_inst

	# Description:
	# Private method that asynchronously runs a QEMU process.
	# Arguments:
	#	run_inst - EmulationInstance object to run
	async def __run_func(run_inst):
		run_inst.proc_res = await asyncio.create_subprocess_shell(run_inst.run_args,
								None,
								asyncio.subprocess.DEVNULL, asyncio.subprocess.DEVNULL)
