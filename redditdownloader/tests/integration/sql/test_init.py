from os.path import isfile, join, abspath
import static.settings as settings
import sql
from tests.mock import EnvironmentTest
import importlib


class SqliteInitTest(EnvironmentTest):
	env = 'rmd_version_4'

	def setUp(self):
		importlib.reload(settings)
		importlib.reload(sql)
		settings.load(self.settings_file)

	def tearDown(self):
		sql.close()
		importlib.reload(settings)

	def test_relative_create(self):
		""" The database should build from relative paths """
		importlib.reload(sql)
		settings.put('output.manifest', './test.sqlite', save_after=False)
		sql.init_from_settings()
		self.assertTrue(isfile(sql.get_file_location()), "Failed to create sqlite file.")

	def test_absolute_create(self):
		""" The database should build from absolute paths """
		importlib.reload(sql)
		settings.put('output.manifest', abspath(join(self.dir, 'test-manifest.sqlite')), save_after=False)
		sql.init_from_settings()
		self.assertTrue(isfile(sql.get_file_location()), "Failed to create sqlite file.")
