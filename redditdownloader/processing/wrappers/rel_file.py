"""
RMD needs a lot of specific File handling and sanitization, and it wants to do it all relative to the Save Directory.
This file exposes a few RelFile classes to assist with this.
"""
import os.path as op
import os
import pathvalidate
import hashlib
import static.filesystem as fs


class RelError(Exception):
	pass


class RelFile:
	def __init__(self, base, file_path=None, full_file_path=None):
		base = op.abspath(base)
		if full_file_path:
			full_file_path = op.abspath(full_file_path)
			if not fs.is_subpath(base, full_file_path):
				raise RelError("The given full file path does not contain the base! {%s}" % full_file_path)
			file_path = op.abspath(full_file_path).replace(base, "", 1)
		file_path = file_path.strip(" ./\\\n\t\r")
		join_test = op.abspath(op.abspath(op.join(base, file_path)))
		if not fs.is_subpath(base, join_test):
			raise RelError("The relative path cannot elevate above the Base Parent: {%s}" % file_path)
		self._base = op.abspath(base)
		self._path = self._norm(file_path)

	def _norm(self, path):
		"""
		File paths should be stored and handled in a cross-platform manner. This normalizes paths.
		"""
		return op.normpath(path).replace("\\", "/")

	def absolute(self):
		return self._norm(op.abspath(op.join(self._base, self._path)))

	def relative(self):
		"""
		Get the relative path of this File, ignoring the base.
		"""
		return self._norm(self._path)

	def exists(self):
		return op.exists(self.absolute())

	def is_file(self):
		return op.isfile(self.absolute())

	def size(self):
		if not self.is_file():
			return 0
		return op.getsize(self.absolute())

	def delete_file(self, recursive_cleanup=True):
		if recursive_cleanup:
			fs.r_unlink(self.absolute())
		else:
			os.remove(self.absolute())

	def abs_hashed(self):
		"""
		Generate an absolute filepath string, replacing the file name with a unique (deterministic) hash.
		Useful where resuming downloads is preferable, but the temp filename may be difficult to otherwise search for.
		"""
		hsh = hashlib.sha1(self.absolute().encode()).hexdigest()
		return self._norm(op.join(op.dirname(self.absolute()), hsh))

	def absolute_base(self):
		return self._norm(op.abspath(self._base))

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
		self._path = self.remove_dotslash(self._path)
		# noinspection PyUnresolvedReferences
		self._path = pathvalidate.sanitize_filepath(self._path, '_').strip(". /\\").strip()
		if not len(self._path):
			self._path = '_'

	def remove_dotslash(self, path):
		np = ''
		while np != path:
			np = path
			path = path.replace('./', '/')
			path = path.replace('/.', '/')
		return path
