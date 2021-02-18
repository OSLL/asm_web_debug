import sys

import gdb_logger
from qemu_run import qemu_runner
from qemu_run_x86_64 import qemu_runner_x86_64
from qemu_run_arm import qemu_runner_arm
from qemu_run_avr import qemu_runner_avr
from gdb_run import gdb_runner
from pprint import pprint

# constants

usage_msg = "Usage: {0} <target architecture> <executable in \"./{1}\" without \".out\">"
prog_dir  = "../demos"


# main module

if __name__ == "__main__":

	def print_usage_str():
		print(usage_msg.format(sys.argv[0], prog_dir))


	if len(sys.argv) < 3:
		print_usage_str()
		exit()

	arg_arch = sys.argv[1]
	arg_exec = sys.argv[2]


	exec_path = "{0}/{1}.{2}.out".format(prog_dir, arg_exec, arg_arch)
	qmrun = qemu_runner.get_by_arch(globals(), arg_arch)
	qmrun.run(exec_path)

	gdbrun = gdb_runner(arg_arch)
	gdbrun.run_and_attach("../gdb_binaries/gdb_" + arg_arch, qmrun)
	while True:
		print("> ", end='')
		gcmd = input()
		resp = gdbrun.write(gcmd)

		print(gdb_logger.get_payload_str(resp, [("stdout", "console"), ("stdout", "log")]), end='')
		if not gdbrun.is_active():
			break

	if gdbrun.gdb_ctrl:
		gdbrun.exit()
