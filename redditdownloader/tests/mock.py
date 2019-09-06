import unittest
import os
from tempfile import gettempdir
from shutil import rmtree
import uuid
import zipfile
import json


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
		cls.dir = os.path.abspath(os.path.join(gettempdir(), randname))
		os.makedirs(cls.dir)
		if not cls.dir or not os.path.isdir(cls.dir):
			cls.dir = None
			raise FileNotFoundError("The test directory was not built!")

	@classmethod
	def tearDownClass(cls):
		if cls.dir:
			rmtree(cls.dir)

	def temp_file(self, filename=None, ext=None):
		""" Generate a temporary filepath scoped within this temp directory. """
		ext = ext if ext else ""
		filename = filename if filename else str(uuid.uuid4())
		return os.path.join(self.dir, "%s.%s" % (filename, ext))


class EnvironmentTest(StagedTest):
	"""
	This type of test imports an encrypted archive, and extracts it into a temporary directory.
	It also supports injecting this temp dir into the settings file extracted, if one exists.
	"""
	env = None
	settings_file = None

	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		src = os.path.abspath(os.path.join(os.path.dirname(__file__), './envs', '%s.zip' % cls.env))
		if not cls.env:
			raise Exception('Environment name is not set for this EnvironmentTest!')
		if not os.path.isfile(src):
			raise Exception('Unknown env file: %s' % src)
		zip_ref = zipfile.ZipFile(src, 'r')
		zip_ref.extractall(cls.dir)  # Extract zip archive.
		zip_ref.close()
		js = os.path.join(cls.dir, 'settings.json')  # Edit "settings.json", if it exists, to insert test dir path.
		if os.path.isfile(js):
			cls.settings_file = js
			with open(js, 'r') as o:
				txt = o.read()
			txt = txt.replace('[TEST_DIR]', json.dumps(cls.dir))
			txt = txt.replace('[REFRESH_TOKEN]', json.dumps(os.environ['RMD_REFRESH_TOKEN']))
			with open(js, 'w') as o:
				o.write(txt)


def mock_handler_request(base_dir, target_url):
	""" Simplify generating a HandlerTask, DownloaderProgress, & RelFile object combo, for Handler tests. """
	import processing.handlers as handlers
	from processing.wrappers import SanitizedRelFile, DownloaderProgress
	filename = str(uuid.uuid4())
	_file = SanitizedRelFile(base=base_dir, file_path=filename)
	_task = handlers.HandlerTask(url=target_url, file_obj=_file)
	_prog = DownloaderProgress()
	return _task, _prog, _file
