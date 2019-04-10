import unittest
import processing.wrappers.http_downloader as http
import processing.wrappers.rel_file as rel
from processing.wrappers import DownloaderProgress


class HttpDownloaderTest(unittest.TestCase):
	def setUp(self):
		self.file = rel.SanitizedRelFile('./', 'test_file')

	def test_download(self):
		prog = DownloaderProgress()
		res = http.download_binary(
			url='https://i.imgur.com/8770jp0.png',
			rel_file=self.file,
			prog=prog,
			handler_id='test-run'
		)
		self.assertTrue(res.success, "The test file failed to download!")
		self.assertIn('.png', self.file.absolute(), "Downloaded invalid filetype!")  # Downloaded a PNG.
		self.assertEqual('100', prog.get_percent(), 'Download did not reach 100%!')

	def test_raw(self):
		html = http.page_text("https://raw.githubusercontent.com/shadowmoose/RedditDownloader/master/Dockerfile")
		self.assertIn("python", html, "Downloaded invalid Raw data from url!")

	def tearDown(self):
		if self.file.exists():
			self.file.delete_file()

