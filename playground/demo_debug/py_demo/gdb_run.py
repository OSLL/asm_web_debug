if __name__ != "__main__":

	from pygdbmi.gdbcontroller import GdbController
	from pygdbmi.constants import GdbTimeoutError

	import gdb_logger
	from pprint import pprint

	class gdb_runner:

		def __init__(self, arch):
			self.arch = arch


		# Method that runs a GDB process, gains control of it through stdin,
		# and attaches it to a specified QEMU process.
		# Arguments:
		#	gdb_exec - full path to gdb executable.
		#	qemu_inst - object of qemu_runner or it's descendant class.
		def run_and_attach(self, gdb_exec, qemu_inst):
			self.gdb_ctrl = GdbController([gdb_exec,
						       "-q", "--interpreter=mi"])
			self.attach(qemu_inst)
		# Method that attaches a GDB process to a specified QEMU process.
		def attach(self, qemu_inst):
			resp = self.gdb_ctrl.write("file "
							+ qemu_inst.cur_exec)
			resp = self.gdb_ctrl.write("target extended-remote localhost:"
							+ str(qemu_inst.dbg_port))

		# Method that sends a commands to GDB process via stdin.
		# Arguments:
		#	command - string representing command.
		# Return value:
		#	payload list of dictionaries.
		def write(self, command):
			resp = self.gdb_ctrl.write(command)
			if command.strip() == "q":
				self.gdb_ctrl = None
			return resp

		# Method that sends to GDB process following commands:
		# - kill the process being debugged.
		# - exit GDB.
		def exit(self):
			write("kill")
			write("q")

		# Method that tells if GDB process is active.
		def is_active(self):
			return self.gdb_ctrl != None
