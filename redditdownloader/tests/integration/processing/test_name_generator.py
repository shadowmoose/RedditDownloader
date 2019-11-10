import static.settings as settings
import sql
from tests.mock import EnvironmentTest
from processing import name_generator as ng
import importlib


class NameGeneratorTest(EnvironmentTest):
	env = 'rmd_staged_db'

	def setUp(self):
		importlib.reload(settings)
		importlib.reload(sql)
		importlib.reload(ng)
		settings.load(self.settings_file)
		sql.init_from_settings()
		self.sess = sql.session()

	def tearDown(self):
		sql.close()

	def test_choose_file_name(self):
		""" Generating a new file name should work """
		tp = self.sess.query(sql.Post).filter(sql.Post.title == 'test').first()
		file = ng.choose_file_name(tp.urls[0], tp, sql.session(), album_size=1)
		self.assertEqual('aww/test - (testuser)', file, msg='Failed to convert basic Test post!')

	def test_existing_file_name(self):
		""" Generating an incremented file name should work """
		tp = self.sess.query(sql.Post).filter(sql.Post.reddit_id == 't3_ahal9v').first()
		file = ng.choose_file_name(tp.urls[0], tp, sql.session(), album_size=1)
		self.assertTrue(file.endswith(' - 2'), msg='Failed to increment duplicate post!')

	def test_album_filename(self):
		""" Generating new & incremented album names should work """
		tp = self.sess.query(sql.Post).join(sql.URL).filter(sql.Post.reddit_id == 't3_98crc8').first()
		file = ng.choose_file_name(tp.urls[0], tp, sql.session(), album_size=1000)
		self.assertEqual('aww/album - (testuser2)/0001', file, msg='Failed to generate new Album foldername!')

		np = self.sess.query(sql.Post).join(sql.URL).filter(sql.Post.reddit_id == 't3_awyf90').first()
		file = ng.choose_file_name(np.urls[0], np, sql.session(), album_size=1)
		self.assertEqual('aww/album - (testuser2) - 2/1', file, msg='Failed to create separate album folder!')

	def test_pattern_loader(self):
		""" All pattern tags should work """
		settings.put('output.file_name_pattern', '[type]-[reddit_id]-[title]-[author]-[subreddit]-[source_alias]-[created_utc]-[created_date]-[created_time]')
		tp = self.sess.query(sql.Post).filter(sql.Post.title == 'test').first()
		file = ng.choose_file_name(tp.urls[0], tp, sql.session(), album_size=1)
		self.assertEqual('Submission-t3_b1rycu-test-testuser-aww-newsource-1552739416-2019-03-16-05.30.16', file, msg='Failed to convert basic Test post!')

	def test_pattern_fail_load(self):
		""" Invalid patterns should fail """
		settings.put('output.file_name_pattern', '[type]-[id]-[title]-[author-[subreddit]-[source_alias]')
		tp = self.sess.query(sql.Post).filter(sql.Post.title == 'test').first()
		with self.assertRaises(Exception, msg='Failed to catch broken pattern!'):
			ng.choose_file_name(tp.urls[0], tp, sql.session(), album_size=1)
