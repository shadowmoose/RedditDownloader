"""
RMD needs a lot of specific File handling and sanitization, and it wants to do it all relative to the Save Directory.
This file exposes a few RelFile classes to assist with this.
"""
import os.path as op
import os
import pathvalidate


class RelError(Exception):
	pass


class RelFile:
	def __init__(self, base, file_path=None, full_file_path=None):
		base = op.abspath(base)
		if full_file_path:
			full_file_path = op.abspath(full_file_path)
			if not self._is_subpath(base, full_file_path):
				raise RelError("The given full file path does not contain the base! {%s}" % full_file_path)
			file_path = op.abspath(full_file_path).replace(base, "", 1)
		file_path = file_path.strip(" ./\\\n\t\r")
		join_test = op.abspath(op.abspath(op.join(base, file_path)))
		if not self._is_subpath(base, join_test):
			raise RelError("The relative path cannot elevate above the Base Parent: {%s}" % file_path)
		self._base = op.abspath(base)
		self._path = self._norm(file_path)

	def _norm(self, path):
		"""
		File paths should be stored and handled in a cross-platform manner. This normalizes paths.
		"""
		return op.normpath(path).replace("\\", "/")

	def _is_subpath(self, base, path):
		base = op.abspath(base)
		path = op.abspath(path)
		while path:
			if path == base:
				return True
			np = op.dirname(path)
			if np == path:
				break
			path = np
		return False

	def absolute(self):
		return self._norm(op.abspath(op.join(self._base, self._path)))

	def relative(self):
		"""
		Get the relative path of this File, ignoring the base.
		"""
		return self._norm(self._path)

	def exists(self):
		return op.exists(self.absolute())

	def set_ext(self, ext):
		""" Sets the file extension at the end of the local path. """
		ext = (''.join([c for c in ext if c.isalnum()])).strip()
		if not ext:
			ext = '.unknown'
		self._path += '.%s' % ext

	def mkdirs(self):
		"""
		Builds the full path to this file, if its parent directories do not exist already.
		"""
		try:
			os.makedirs(op.dirname(self.absolute()), exist_ok=True)
		except OSError:
			pass

	def __str__(self):
		return self.absolute()


class SanitizedRelFile(RelFile):
	def __init__(self, base, file_path=None, full_file_path=None):
		super().__init__(base, file_path, full_file_path)
		self._path = pathvalidate.sanitize_filepath(self._path.replace("..", ""))
		if not len(self._path.strip(". /\\")):
			raise RelError("File path is too short! {%s}" % file_path)


if __name__ == '__main__':
	rf = SanitizedRelFile(base="C:/Users", file_path="t/./test/[title].txt")
	print('Absolute:', rf.absolute())
	print('Relative:', rf.relative())
