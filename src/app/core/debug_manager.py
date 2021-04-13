from pygdbmi.gdbcontroller import GdbController

from pprint import pprint

class DebugManager:

	# Constants:


	arch_run_cmds =  {
				"default": ["gdb"]
			 }
	arch_run_flags = {
				"default": ["-q", "--interpreter=mi"]
			 }

	# Static fields:

	# Dictionary of GDB instances, should only contain pairs in from of:
	# {uuid [int] : [GdbController]}
	gdb_instances = {}

	# Static methods:

	# Description:
	# Create a GDB process, gains control of it, and attaches it to a specified executable through
	# a TCP connection.
	#	run_inst - EmulationInstance object to attach to.
	#	arch - target architecture
	def run_and_attach(run_inst, arch):

		if arch in DebugManager.arch_run_cmds:
			run_cmds = DebugManager.arch_run_cmds[arch]
		else:
			run_cmds = DebugManager.arch_run_cmds["default"]
		if arch in DebugManager.arch_run_flags:
			run_flags = DebugManager.arch_run_flags[arch]
		else:
			run_flags = DebugManager.arch_run_flags["default"]

		DebugManager.gdb_instances[run_inst.code_id] = GdbController(run_cmds.extend(run_flags))
		gdb_ctrl = DebugManager.gdb_instances[run_inst.code_id]

		res = gdb_ctrl.write("file " + run_inst.exec_fname)
		res.extend(gdb_ctrl.write("target extended-remote localhost:" + str(run_inst.debug_port)))
		res.extend(gdb_ctrl.write("run"))
		pprint(res)
		return res
