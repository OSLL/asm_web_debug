from pygdbmi.gdbcontroller import GdbController
from pygdbmi.constants import GdbTimeoutError
from pprint import pprint

import sys
import asyncio

# constants

usage_msg = "Usage: {0} <target architecture> <executable in \"./{1}\" without \".out\">"
prog_dir  = "demos"

avr_flags = "-machine mega -display none"

dflags = "-g 1234"
avr_dflags = "-s -S"

# functions

def print_usage_str():
	print(usage_msg.format(sys.argv[0], prog_dir))

async def run_qemu(arch, execf):
	if arch == "avr":
		qemu_cmd = "qemu-system-avr {0} {1} -bios {2}/{3}.{4}.out".format(
				avr_flags, avr_dflags, prog_dir, execf, arch)
	else:
		qemu_cmd = "qemu-{0} {1} {2}/{3}.{0}.out".format(
				arch, dflags, prog_dir, execf)

	proc = await asyncio.create_subprocess_shell(qemu_cmd)

solidify_esc_seq__esc_sqs = [['t', '\t'], ['n', '\n'], ['r', '\r']]
def solidify_esc_seq(in_str):
	for esc_seq in solidify_esc_seq__esc_sqs:
		in_str = in_str.replace("\\" + esc_seq[0], esc_seq[1])
	return in_str

def get_console_payload_str(response):
	pl_str = ""
	for pl in response:
		if  "stream" in pl.keys() and pl["stream"] == "stdout"\
		and "type"   in pl.keys() and pl["type"]   == "console":
			pl_str += solidify_esc_seq(pl["payload"].replace("\\\\", "\\"))
	return pl_str


# main module
if len(sys.argv) < 3:
	print_usage_str()
	exit()

# CLI arguments
arg_arch = sys.argv[1]
arg_exec = sys.argv[2]

asyncio.run(run_qemu(arg_arch, arg_exec))

gdbc = GdbController(["./gdb_binaries/gdb_{0}".format(arg_arch),
			"-q", "--interpreter=mi"])

print("Running GDB:\n")

print("Setting target executable file")
resp = gdbc.write("file ./{0}/{1}.{2}.out".format(prog_dir, arg_exec, arg_arch))
#pprint(resp)

print("Connecting to debug session")
resp = gdbc.write("target extended-remote localhost:1234")
#pprint(resp)

print("Successfully connected\n")
while True:
	print("> ", end='')
	cmd = input()
	try:
		resp = gdbc.write(cmd)
		if cmd == 'q':
			break
		print(get_console_payload_str(resp))
		#pprint(resp)
	except GdbTimeoutError:
		print("gdb didn't send a response, exiting")
		break

