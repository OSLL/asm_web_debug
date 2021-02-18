if __name__ != "__main__":

	from qemu_run import qemu_runner

	class qemu_runner_arm(qemu_runner):

		def __init__(self):
			super().__init__()
			self.arch = "arm"
