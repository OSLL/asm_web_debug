if __name__ != "__main__":

	from ld_run import ld_runner

	class ld_runner_avr(ld_runner):

		def __init__(self):
			super().__init__()
			self.run_flags = ["-m", "avr6"]
			self.exec_path = "avr-ld"
