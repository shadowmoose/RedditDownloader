from tests.mock import StagedTest, mock_handler_request
from processing.handlers import direct_link


class DirectHandlerTest(StagedTest):
	def test_direct_reddit(self):
		""" Simple direct image download """
		_task, _prog, _file = mock_handler_request(self.dir, 'https://i.redd.it/lasm5nl33o4x.png')
		res = direct_link.handle(_task, _prog)
		self.assertTrue(res, "redd.it png download failed!")
		self.assertTrue(_file.exists(), "redd.it png was not downloaded! %s" % res.failure_reason)
		self.assertIn('.png', _file.relative(), "redd.it png is missing extension!")

	def test_404_download(self):
		""" Invalid URLs should fail """
		_task, _prog, _file = mock_handler_request(self.dir, 'https://i.redd.it/lasm5nl33o4asdfx.png')
		res = direct_link.handle(_task, _prog)
		self.assertTrue(res, "Invalid response after failed download!")
		self.assertFalse(_file.exists(), "A file was created for an invalid URL!")
		self.assertFalse(res.success, "This invalid URL was supposed to fail!")
		self.assertIn('404', res.failure_reason, "The handler did not include the HTTP error code!")

	def test_non_media(self):
		""" Links to non-media should be skipped """
		_task, _prog, _file = mock_handler_request(self.dir, 'https://raw.githubusercontent.com/shadowmoose/RedditDownloader/master/README.md')
		res = direct_link.handle(_task, _prog)
		self.assertFalse(res, "A non-media file was not skipped!")
		self.assertFalse(_file.exists(), "A file was created for an invalid URL!")

