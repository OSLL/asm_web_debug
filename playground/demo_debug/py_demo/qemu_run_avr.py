if __name__ != "__main__":

	from qemu_run import qemu_runner
	import socket_util
	import asyncio

	class qemu_runner_avr(qemu_runner):

		def __init__(self):
			super().__init__()
			self.arch = "avr"


		async def __run_func(self, exec_path):
			qemu_cmd = "qemu-system-avr {0} -bios {1}".format(
					self.run_flags, exec_path)
			self.proc = await asyncio.create_subprocess_shell(qemu_cmd)

		def run(self, exec_path):
			self.cur_exec = exec_path
			self.run_flags += "-machine mega -display none"
			self.dbg_port = socket_util.probe_for_port("localhost")
			if self.dbg_port == None:
				return False
			self.run_flags += " -S -gdb tcp::" + str(self.dbg_port)
			asyncio.run(self.__run_func(exec_path))
