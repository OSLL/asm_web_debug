import os

class SourceCodeContainer:
	""" source code container """

	def __init__(self, source_dir):
		self.def_user_src_name = "main.S"

		self.src_dir_path = self.mkdir(source_dir)


	def save_solution(self, uid, code):
		if self.is_solution_exists(uid):
			raise FileExistsError("Source file with uid " + str(uid) + " already exists")

		self.mkdir(self.src_dir_path  + str(uid))
		
		try:
			with open(self.full_path(uid) + self.def_user_src_name, "w") as file:
				file.write(code)

		except OSError:
			raise OSError("SourceCodeContainer.save_solution write file exception")


	def is_solution_exists(self, uid):
		return os.path.exists(self.src_dir_path + str(uid))


	def full_path(self, uid):
		return os.path.abspath(self.src_dir_path + str(uid)) + "/"

	
	def mkdir(self, name):
		path = "./"

		for eld in name.split("/"):
			path = path + eld + "/"

			if not os.path.isdir(path):
				os.mkdir(path)

		return path
