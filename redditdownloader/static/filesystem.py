from os.path import join, dirname, exists, abspath
from os import makedirs, getcwd, unlink, removedirs
from appdirs import AppDirs
import static.metadata as metadata


app_base = AppDirs('RMD', metadata.pypy_name).user_data_dir
project_base = abspath(join(dirname(abspath(__file__)), '../../'))


def find_file(name):
	"""
	Find the full path to the given file,
	checking locally first - then defaulting to the user storage location.

	:param name: The base name of the file.
	:return: The full path to the given file, possibly defaulting to a missing location.
	"""
	locs = [getcwd(), app_base]
	for l in locs:
		fp = join(abspath(l), name)
		if exists(fp):
			return fp
	return join(abspath(app_base), name)


def mkpath(path):
	"""
	Build the subdirectory chain required to safely create the given file path.
	The path should lead to a file, and not a directory.
	"""
	return makedirs(dirname(path), exist_ok=True)


def copen(file, mode='r', autofind=False):
	"""
	Open the given file for reading or writing, creating the subdirectory path if needed.

	:param file: The file to open.
	:param mode: The mode to open the file with.
	:param autofind: If True, use `find_file` to locate the filename.
	:return: The handle of the opened File.
	"""
	file_path = find_file(file) if autofind else abspath(file)
	if any(m in mode for m in ['w', 'a']):
		mkpath(file_path)
	return open(file_path, mode)


def is_subpath(base, path):
	base = abspath(base)
	path = abspath(path)
	while path:
		if path == base:
			return True
		np = dirname(path)
		if np == path:
			break
		path = np
	return False


def r_unlink(path):
	"""
	Deletes the given file, then removes any empty parent dirs recursively.

	:param path: The path to the file that should be deleted.
	"""
	unlink(path)
	try:
		removedirs(dirname(path))
	except OSError:
		pass
