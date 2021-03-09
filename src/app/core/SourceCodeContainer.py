
import os
import random

class SourceCodeContainer:
	""" source code container """

	def __init__(self, source_dir):
		self.src_dir_path = source_dir

		if not os.path.isdir(source_dir):
			raise OSError


	def saveSolution(self, uid, code):

		if self.isSolutionExists(uid):
			raise FileExistsError
		
		try:
			with open(self.path(uid), "w") as file:
				file.write(code)
		
		except OSError:
			raise OSError
		except:
			pass


	def isSolutionExists(self, uid):
		return os.path.exists(self.path(uid))

	
	def path(self, uid):
		return self.src_dir_path + str(uid) + ".S"


	def fullPath(self, uid):
		return os.path.abspath(self.path(uid))