import json
import importlib
import static.settings as settings
import sql
from tests.mock import EnvironmentTest


class SqlitePostSearcherTest(EnvironmentTest):
	env = 'rmd_staged_db'

	def setUp(self):
		importlib.reload(sql)
		self.assertFalse(sql._engine, msg="Failed to clear SQL session.")
		settings.load(self.settings_file)
		sql.init_from_settings()
		self.ps = sql.PostSearcher(sql.session())

	def tearDown(self):
		sql.close()

	def test_init_db(self):
		""" PostSearcher should find all valid fields """
		self.assertGreater(len(self.ps.get_searchable_fields()), 1, msg="Didn't find enough searchable fields!")
		for f in self.ps.get_searchable_fields():
			self.assertIn(f, sql.Post.__dict__.keys(), msg="Invalid searchable field!")
			self.assertFalse(f.startswith('_'), msg='Invalid field was detected: %s' % f)

	def test_post_search_author(self):
		""" Posts should be searchable """
		posts = self.ps.search_fields(['author'], 'testuser')
		self.assertEqual(len(posts), 1, msg="Found incorrect number of posts!")

	def test_empty_post_search(self):
		""" Empty results are possible """
		posts = self.ps.search_fields(['author'], 'bhaser')
		self.assertEqual(0, len(posts), msg="Found incorrect number of posts!")

	def test_invalid_search(self):
		""" Searchable fields should be limited """
		posts = self.ps.search_field_conditions(['__dict__'], 'test')
		self.assertEqual(0, len(posts), msg="Invalid search term was allowed!")

	def test_all_search_params(self):
		""" All valid fields should search """
		for f in self.ps.get_searchable_fields():
			posts = self.ps.search_field_conditions([f], 'testuser')
			self.assertEqual(1, len(posts), msg="Failed to generate search term for '%s'!" % f)

	def test_post_json_encode(self):
		""" Posts should serialize """
		posts = self.ps.search_fields(['type'], 'Submission')
		self.assertGreater(len(posts), 0, msg="Didn't find enough Posts to test!")
		ser = sql.encode_safe(posts, stringify=True, indent=4)  # Encode Post results to JSON string.
		arr = json.loads(ser)  # Decode the JSON string os Posts.
		self.assertGreater(len(arr), 0, msg='Failed to decode array of posts.')
		for p in arr:
			for f in self.ps.get_searchable_fields():
				self.assertIn(f, p, msg='Field was missing from decoded Post: %s' % f)

	def test_full_encode(self):
		""" The entire nested relation should serialize """
		p = sql.session().query(sql.Post).join(sql.URL).join(sql.File).first()
		self.assertTrue(p, msg='Failed to find a test Post.')
		for u in p.urls:
			self.assertTrue(u.file, msg="URL is missing a file! %s" % u)  # These are lazy loaded, so check them all.
		ser = sql.encode_safe(p)

		self.assertTrue(ser, msg='Failed to properly encode full stack Post into Object!')
		self.assertGreater(len(ser['urls']), 0, msg='Lost Post URLs in encode!')
		for u in ser['urls']:
			self.assertIn('file', u, msg='Lost file in URL encode! %s' % u)
