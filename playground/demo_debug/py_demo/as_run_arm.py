if __name__ != "__main__":

	from as_run import as_runner

	class as_runner_arm(as_runner):

		def __init__(self):
			super().__init__()
			self.exec_path = "arm-linux-gnueabi-as"
