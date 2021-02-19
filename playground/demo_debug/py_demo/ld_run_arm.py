if __name__ != "__main__":

	from ld_run import ld_runner

	class ld_runner_arm(ld_runner):

		def __init__(self):
			super().__init__()
			self.exec_path = "arm-linux-gnueabi-ld"
