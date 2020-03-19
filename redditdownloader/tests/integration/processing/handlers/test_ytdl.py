from tests.mock import StagedTest, mock_handler_request
from processing.handlers import ytdl


class YTDLHandlerTest(StagedTest):
	""" Test the YT_DL Handler's downloading capabilities """

	def test_gfycat(self):
		""" Attempt Gfycat.com download """
		_task, _prog, _file = mock_handler_request(self.dir, 'https://gfycat.com/sarcasticfixedanemoneshrimp')
		res = ytdl.handle(_task, _prog)
		self.assertTrue(res, "Failed to download Gfycat video!")
		self.assertTrue(_file.exists(), "Gfycat video was not downloaded! %s" % res.failure_reason)
		self.assertTrue(_file.relative().endswith('.mp4'), 'Failed to use .mp4 extension for video file!')

	def test_youtube(self):
		""" Attempt Youtube download """
		_task, _prog, _file = mock_handler_request(self.dir, 'https://www.youtube.com/watch?v=8URukvnUYTw')
		res = ytdl.handle(_task, _prog)
		self.assertTrue(res, "Failed to download YouTube video!")
		self.assertTrue(_file.exists(), "YouTube video was not downloaded! %s" % res.failure_reason)
		self.assertTrue('.' in _file.relative(), "YTDL failed to apply file extension! (%s)" % _file.absolute())
		self.assertTrue('unknown' not in _file.relative(), 'Invalid name for video file! (%s)' % _file.absolute())

