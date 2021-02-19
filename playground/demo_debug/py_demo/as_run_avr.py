if __name__ != "__main__":

	from as_run import as_runner

	class as_runner_avr(as_runner):

		def __init__(self):
			super().__init__()
			self.run_flags = ["-g", "-mmcu=avr6"]
			self.exec_path = "avr-as"
