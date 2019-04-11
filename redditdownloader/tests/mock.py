import unittest
import os
from tempfile import gettempdir
from shutil import rmtree
import uuid


class Object:
	def __init__(self, **kwargs):
		for k, v in kwargs.items():
			setattr(self, k, v)


class StagedTest(unittest.TestCase):
	""" This Test type utilizes a staged environment, which is automatically setup and torn down. """
	dir = None

	@classmethod
	def setUpClass(cls):
		randname = 'rmd-test-%s' % uuid.uuid4()
		cls.dir = os.path.join(gettempdir(), randname)
		os.makedirs(cls.dir)
		if not cls.dir or not os.path.isdir(cls.dir):
			raise FileNotFoundError("The test directory was not built!")

	@classmethod
	def tearDownClass(cls):
		rmtree(cls.dir, ignore_errors=True)

	def temp_file(self, filename=None, ext=None):
		""" Generate a temporary filepath scoped within this temp directory. """
		ext = ext if ext else ""
		filename = filename if filename else str(uuid.uuid4())
		return os.path.join(self.dir, "%s.%s" % (filename, ext))


def mock_handler_request(base_dir, target_url):
	""" Simplify generating a HandlerTask, DownloaderProgress, & RelFile object combo, for Handler tests. """
	import processing.handlers as handlers
	from processing.wrappers import SanitizedRelFile, DownloaderProgress
	filename = str(uuid.uuid4())
	_file = SanitizedRelFile(base=base_dir, file_path=filename)
	_task = handlers.HandlerTask(url=target_url, file_obj=_file)
	_prog = DownloaderProgress()
	return _task, _prog, _file
