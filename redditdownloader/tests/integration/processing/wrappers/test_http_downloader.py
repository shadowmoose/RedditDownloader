import processing.wrappers.http_downloader as http
import processing.wrappers.rel_file as rel
from processing.wrappers import DownloaderProgress
from tests.mock import StagedTest


class HttpDownloaderTest(StagedTest):

	def test_binary(self):
		""" Download a binary file """
		file = rel.SanitizedRelFile(self.dir, 'test_file')
		prog = DownloaderProgress()
		res = http.download_binary(
			url='https://i.imgur.com/8770jp0.png',
			rel_file=file,
			prog=prog,
			handler_id='test-run'
		)
		self.assertTrue(res.success, "The test file failed to download!")
		self.assertTrue(file.exists(), "Failed to download the test binary!")
		self.assertIn('.png', file.absolute(), "Downloaded invalid filetype!")  # Downloaded a PNG.
		self.assertEqual('100', prog.get_percent(), 'Download did not reach 100%!')

	def test_raw(self):
		""" Read raw page text """
		html = http.page_text("https://raw.githubusercontent.com/shadowmoose/RedditDownloader/master/Dockerfile")
		self.assertIn("python", html, "Downloaded invalid Raw data from url!")

	def test_media_identify(self):
		""" Downloader should ID valid media URLs """
		ftype, httpstat = http.is_media_url("https://i.imgur.com/jIuIbIu.gif", return_status=True)
		self.assertEqual(httpstat, 200, "Test link did not return http 200! (%s)" % httpstat)
		self.assertTrue(ftype, "Did not correctly identify image file!")

	def test_invalid_media_identify(self):
		""" Downloader should ID invalid URLs """
		ftype = http.is_media_url("https://raw.githubusercontent.com/shadowmoose/RedditDownloader/master/Dockerfile")
		self.assertFalse(ftype, "Did not correctly identify image file!")
