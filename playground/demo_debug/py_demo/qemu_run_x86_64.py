if __name__ != "__main__":

	from qemu_run import qemu_runner

	class qemu_runner_x86_64(qemu_runner):

		def __init__(self):
			super().__init__()
			self.arch = "x86_64"
