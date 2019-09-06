import static.settings as settings
from tests.mock import EnvironmentTest
from interfaces.terminal import TerminalUI
from os.path import join, isfile
import os
import sql
import unittest

download_ran = False
session = None


@unittest.skipIf('GITHUB_ACTION' in os.environ, "Cannot reliably test full download on GitHub's internet.")
class TerminalDownloadTest(EnvironmentTest):
	env = 'controlled_sources'

	def setUp(self):
		global download_ran, session
		if not download_ran:
			download_ran = True
			settings.load(self.settings_file)
			tui = TerminalUI('test_version')
			tui.display()
			self.db_path = join(settings.get('output.base_dir'), 'manifest.sqlite')
			sql.init_from_settings()
			session = sql.session()

	def tearDown(self):
		sql.close()

	def test_db_exists(self):
		""" The Database file should be created """
		self.assertTrue(isfile(self.db_path), 'The Database was not created!')

	def test_db_posts(self):
		""" Posts should have been located """
		cnt = len(session.query(sql.Post).all())
		self.assertGreater(cnt, 0, 'No Posts were added to the DB!')

	def test_db_urls(self):
		""" URLs should have been located """
		cnt = len(session.query(sql.URL).all())
		self.assertGreater(cnt, 0, 'No URLs were added to the DB!')

	def test_db_files(self):
		""" Files should have been located """
		cnt = len(session.query(sql.File).all())
		self.assertGreater(cnt, 0, 'No Files were added to the DB!')

	def test_files_exist(self):
		""" All Files marked as downloaded should exist """
		files = session.query(sql.File).filter(sql.File.downloaded).all()
		for f in files:
			path = join(settings.get('output.base_dir'), f.path)
			self.assertTrue(isfile(path), "File does not exist: %s" % path)

	def test_urls_processed(self):
		""" All URLS should have been processed """
		urls = session.query(sql.URL).all()
		for u in urls:
			self.assertTrue(u.processed, 'A URL was not processed: %s' % u.address)

	def test_urls_albums(self):
		""" All album URLs should have children """
		urls = session.query(sql.URL).filter(sql.URL.album_id).filter(sql.URL.album_is_parent).all()
		ch = session.query(sql.URL).filter(sql.URL.album_id).filter(sql.URL.album_is_parent == False).all()
		self.assertGreater(len(urls), 0, 'No parent album URLs were downloaded!')
		self.assertGreater(len(ch), 0, 'No children album URLS were found.')
		for u in urls:
			children = session.query(sql.URL).filter(sql.URL.album_id).filter(sql.URL.album_is_parent == False).all()
			self.assertGreater(len(children), 0, 'An album parent has no children: %s' % u.address)

	def test_url_files(self):
		""" Album parent Files should be properly downloaded or ignored """
		urls = session.query(sql.URL).all()
		for u in urls:
			if u.album_is_parent:
				self.assertFalse(u.file.downloaded, "An Album Parent URL has a file attached: %s" % u)
			else:
				self.assertTrue(u.file.downloaded, "A child URL has no File: %s" % u)

	def test_file_hashes(self):
		""" All downloaded Files should have a hash from deduplication """
		urls = session.query(sql.URL).filter(sql.URL.album_id == None).all()
		files = [u.file for u in urls]
		self.assertGreater(len(files), 0, 'No non-album files were located!')
		for f in files:
			if f.downloaded:
				self.assertTrue(f.hash, 'File is missing a hash: %s' % f)
