import os


class SourceManager:
	""" source code container """

	@classmethod
	def init(cls, source_dir):
		cls.def_user_src_name = "main.S"
		cls.src_dir_path = source_dir

		if len(source_dir) == 0:
			raise Exception('arg zero length exception')

		if cls.src_dir_path[-1] != '/':
			cls.src_dir_path = self.src_dir_path  + '/'

		cls.mkdir(cls.src_dir_path)

	@classmethod
	def save_code(cls, uid, code):
		cls.mkdir(cls.src_dir_path + str(uid))
		
		try:
			with open(f'{cls.full_path(uid)}{cls.def_user_src_name}', "w", encoding="utf-8") as file:
				file.write(code)

		except OSError:
			raise OSError("write file exception")

	@classmethod
	def get_code(cls, uid):
		source_code = ''
		source_file_name = f'{cls.full_path(uid)}{cls.def_user_src_name}'

		if not cls.is_code_exists(uid):
			raise OSError("Subdir with uid " + str(uid) + " doesn't exist")

		if not os.path.isfile(source_file_name):
			raise OSError("Source file [" + source_file_name + "] in subdir " + str(uid) + " not found")

		with open(source_file_name, "r", encoding="utf-8") as file:
			source_code = file.read()

		return source_code

	@classmethod
	def is_code_exists(cls, uid):
		return os.path.exists(cls.src_dir_path + str(uid))

	@classmethod
	def full_path(cls, uid):
		ans = os.path.abspath(cls.src_dir_path + str(uid)) + "/"
		if not os.path.isdir(ans):
			raise OSError("the solution with the specified id does not exist")
		else:
			return ans

	@classmethod
	def get_code_file_path(cls, uid):
		return f'{cls.full_path(uid)}/{cls.def_user_src_name}'

	@staticmethod
	def mkdir(name):
		if not os.path.exists(name):
			os.makedirs(name)
