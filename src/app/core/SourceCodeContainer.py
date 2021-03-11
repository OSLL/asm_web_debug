import os
import random


class SourceCodeContainer:
	""" source code container """

	def __init__(self, source_dir):
		self.def_user_src_name = "main.S"

		self.src_dir_path = self.mkdir(source_dir)


	def save_solution(self, uid, code):
		self.mkdir(self.src_dir_path + str(uid))
		
		try:
			with open(self.full_path(uid) + self.def_user_src_name, "w") as file:
				file.write(code)

		except OSError:
			raise OSError("SourceCodeContainer.save_solution write file exception")


	def is_solution_exists(self, uid):
		return os.path.exists(self.src_dir_path + str(uid))


	def full_path(self, uid):
		ans = os.path.abspath(self.src_dir_path + str(uid)) + "/"
		if not os.path.isdir(ans):
			raise OSError("the solution with the specified id does not exist")
		else:
			return ans

	
	def mkdir(self, name):
		path = "./"

		for eld in name.split("/"):
			path = path + eld + "/"

			if not os.path.isdir(path):
				os.mkdir(path)

		return path

	
	def gen_free_uid(self):
		uid = 0

		while True:
			uid = random.randint(100000000, 999999999)

			if not self.is_solution_exists(uid):
				yield uid



