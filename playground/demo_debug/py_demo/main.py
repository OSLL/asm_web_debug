import sys

import gdb_logger
from qemu_run import qemu_runner
from gdb_run import gdb_runner
from as_run import as_runner
from ld_run import ld_runner

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


	s_path = "{0}/{1}.{2}.s".format(prog_dir, arg_exec, arg_arch)
	o_path = "{0}/{1}.{2}.o".format(prog_dir, arg_exec, arg_arch)
	out_path = "{0}/{1}.{2}.out".format(prog_dir, arg_exec, arg_arch)

	asrun = as_runner(arg_arch)
	resp = asrun.run(s_path, o_path)
	print(str(resp.stdout)[2:-1])
	print(str(resp.stderr)[2:-1])
	if resp.returncode != 0:
		exit(resp.returncode)
	ldrun = ld_runner(arg_arch)
	resp = ldrun.run(o_path, out_path)
	print(str(resp.stdout)[2:-1])
	print(str(resp.stderr)[2:-1])
	if resp.returncode != 0:
		exit(resp.returncode)

	qmrun = qemu_runner(arg_arch)
	qmrun.run(out_path)

	gdbrun = gdb_runner(arg_arch)
	resp = gdbrun.run_and_attach("../gdb_binaries/gdb_" + arg_arch, qmrun)
	print(gdb_logger.get_payload_str(resp, [("stdout", "console"), ("stdout", "log")]), end='')
	while True:
		print("> ", end='')
		gcmd = input()
		resp = gdbrun.write(gcmd)

		print(gdb_logger.get_payload_str(resp, [("stdout", "console"), ("stdout", "log")]), end='')
		if not gdbrun.is_active():
			break

	if gdbrun.gdb_ctrl:
		gdbrun.exit()
