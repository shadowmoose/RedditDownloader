from tests.mock import StagedTest, mock_handler_request
from processing.handlers import imgur
from static import settings
import os


class ImgurHandlerTest(StagedTest):
	""" Test the Imgur Handler's downloading capabilities """

	def setUp(self):
		settings.put('imgur.client_id', os.environ['RMD_IMGUR_ID'])
		settings.put('imgur.client_secret', os.environ['RMD_IMGUR_SECRET'])

	def test_correct_urls(self):
		""" Handler should be able to identify valid Imgur URLs """
		test_urls = {
			# Potentially valid URLS:
			'imgur.com/test': True,
			'https://www.imgur.com/album': True,
			'http://i.imgur.com/album': True,
			'https://m.imgur.com/album': True,
			'm.imgur.com/album': True,
			'i.imgur.com/album': True,
			'https://i.imgur.com/8770jp0.png': True,
			'//imgur.com/test': True,
			# Invalid URLS:
			'not-imgur.com/test': False,
			'imgur.com.fake/test': False,
			'imgur.org/test': False,
			'https://imgur.org': False,
			'https://not-imgur.com': False,
			'https://google.com': False,
			'imgur': False
		}
		for url, valid in test_urls.items():
			clean = imgur.is_imgur(url)
			self.assertEqual(valid, bool(clean), "Imgur improperly handled a test URL: [%s]->(%s)" % (url, clean))

	def test_gallery(self):
		""" Attempt Imgur gallery Download """
		_task, _prog, _file = mock_handler_request(self.dir, 'https://imgur.com/gallery/plN58')
		res = imgur.handle(_task, _prog)
		self.assertTrue(res, "Imgur gallery search failed!")
		self.assertTrue(res.success, "Imgur gallery failed to download: %s" % res.failure_reason)
		self.assertEqual(len(res.album_urls), 134, "Handler didn't find all gallery URLS!")

	def test_invalid_album(self):
		""" Attempt to download an Animation, which (improperly) has an album prefix """
		_task, _prog, _file = mock_handler_request(self.dir, 'https://imgur.com/a/KEVkAWf')
		res = imgur.handle(_task, _prog)
		self.assertTrue(res, "Imgur album download failed!")
		self.assertTrue(_file.exists(), "Imgur album animation was not downloaded! %s" % res.failure_reason)
		self.assertIn('.mp4', _file.relative(), "Imgur downloaded the wrong animation format from album!")

	def test_direct_png(self):
		""" Test a simple direct image download """
		_task, _prog, _file = mock_handler_request(self.dir, 'https://i.imgur.com/8770jp0.png')
		res = imgur.handle(_task, _prog)
		self.assertTrue(res, "Imgur png download failed!")
		self.assertTrue(_file.exists(), "Imgur png was not downloaded! %s" % res.failure_reason)
		self.assertIn('.png', _file.relative(), "Imgur png is missing extension!")

	def test_indirect_link(self):
		""" Test an indirect png download """
		_task, _prog, _file = mock_handler_request(self.dir, 'https://i.imgur.com/8770jp0')
		res = imgur.handle(_task, _prog)
		self.assertTrue(res, "Imgur indirect png download failed!")
		self.assertTrue(_file.exists(), "Imgur indirect png was not downloaded! %s" % res.failure_reason)
		self.assertIn('.png', _file.relative(), "Imgur indirect image is missing png extension!")

	def test_gif(self):
		""" Test gif download """
		_task, _prog, _file = mock_handler_request(self.dir, 'imgur.com/r/gifs/jIuIbIu')
		res = imgur.handle(_task, _prog)
		self.assertTrue(res, "Imgur gif download failed!")
		self.assertTrue(_file.exists(), "Imgur gif was not downloaded! %s" % res.failure_reason)
		self.assertTrue(_file.relative().endswith('.mp4'), 'Failed to use .mp4 extension for .gif file!')

	def test_gifv(self):
		""" Test gifv download """
		_task, _prog, _file = mock_handler_request(self.dir, 'https://imgur.com/MVPdV4a')
		res = imgur.handle(_task, _prog)
		self.assertTrue(res, "Imgur gifv download failed!")
		self.assertTrue(_file.exists(), "Imgur gifv was not downloaded! %s" % res.failure_reason)
		self.assertTrue(_file.relative().endswith('.mp4'), 'Failed to use .mp4 extension for .gifv file!')
