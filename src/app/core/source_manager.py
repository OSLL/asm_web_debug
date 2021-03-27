import os


class SourceManager:
	""" source code container """

	def __init__(self, source_dir):
		self.def_user_src_name = "main.S"
		self.src_dir_path = source_dir

		if len(source_dir) == 0:
			raise Exception('arg zero length exception')

		if self.src_dir_path[-1] != '/':
			self.src_dir_path = self.src_dir_path  + '/'

		self.mkdir(self.src_dir_path)


	def save_code(self, uid, code):
		self.mkdir(self.src_dir_path + str(uid))
		
		try:
			with open(f'{self.full_path(uid)}{self.def_user_src_name}', "w", encoding="utf-8") as file:
				file.write(code)

		except OSError:
			raise OSError("write file exception")

	
	def get_code(self, uid):
		source_code = ''
		source_file_name = f'{self.full_path(uid)}{self.def_user_src_name}'

		if not self.is_code_exists(uid):
			raise OSError("Subdir with uid " + str(uid) + " doesn't exist")

		if not os.path.isfile(source_file_name):
			raise OSError("Source file [" + source_file_name + "] in subdir " + str(uid) + " not found")

		with open(source_file_name, "r", encoding="utf-8") as file:
			source_code = file.read()

		return source_code


	def is_code_exists(self, uid):
		return os.path.exists(self.src_dir_path + str(uid))


	def full_path(self, uid):
		ans = os.path.abspath(self.src_dir_path + str(uid)) + "/"
		if not os.path.isdir(ans):
			raise OSError("the solution with the specified id does not exist")
		else:
			return ans


	def get_code_file_path(self, uid):
		return f'{self.full_path(uid)}{self.def_user_src_name}'

	
	def mkdir(self, name):
		if not os.path.exists(name):
			os.makedirs(name)




