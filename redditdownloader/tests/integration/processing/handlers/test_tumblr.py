from tests.mock import StagedTest, mock_handler_request
from processing.handlers import tumblr


class TumblrHandlerTest(StagedTest):
	""" Test the Tumblr Handler's downloading capabilities """

	def test_gallery(self):
		""" Attempt Tumblr gallery Download """
		_task, _prog, _file = mock_handler_request(self.dir, 'https://theshadowmoose.tumblr.com/post/184562233420/test-rmd-image-upload')
		res = tumblr.handle(_task, _prog)
		self.assertTrue(res, "Tumblr gallery search failed! %s" % res.failure_reason)
		self.assertEqual(len(res.album_urls), 2, "Handler didn't find all gallery URLS!")

	def test_video(self):
		""" Test embedded video download """
		_task, _prog, _file = mock_handler_request(self.dir, 'theshadowmoose.tumblr.com/post/184562318724/another-test-post-with-video')
		res = tumblr.handle(_task, _prog)
		self.assertTrue(res, "Tumblr video download failed!")
		self.assertTrue(_file.exists(), "Tumblr video was not downloaded! %s" % res.failure_reason)
		self.assertTrue(_file.relative().endswith('.mp4'), 'Failed to use .mp4 extension for video file!')

	def test_text_post(self):
		""" Test invalid post parsing """
		_task, _prog, _file = mock_handler_request(self.dir, 'http://theshadowmoose.tumblr.com/post/184562766360/test-text-post-rmd')
		res = tumblr.handle(_task, _prog)
		self.assertFalse(res, "Tumblr downloaded something from a text post!")
		self.assertFalse(_file.exists(), "Tumblr downloaded a file from a text post!")
