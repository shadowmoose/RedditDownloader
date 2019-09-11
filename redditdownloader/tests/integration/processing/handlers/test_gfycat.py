from tests.mock import StagedTest, mock_handler_request
from processing.handlers import gfycat


class GfycatTest(StagedTest):
	def test_direct_reddit(self):
		""" Simple direct link download """
		_task, _prog, _file = mock_handler_request(self.dir, 'https://gfycat.com/heftyinnocentelephantbeetle')
		res = gfycat.handle(_task, _prog)
		self.assertTrue(res, "gfycat webm download failed!")
		self.assertTrue(_file.exists(), "gfycat webm was not downloaded! %s" % res.failure_reason)
		self.assertIn('.webm', _file.relative(), "gfycat webm is missing extension!")

	def test_invalid_url(self):
		""" Invalid gfycat URLs should fail """
		_task, _prog, _file = mock_handler_request(self.dir, 'https://gfycat.com/ripemadintermediateINVALID')
		res = gfycat.handle(_task, _prog)
		self.assertIs(res, False, "Invalid response after failed download!")
		self.assertFalse(_file.exists(), "A file was created for an invalid URL!")

	def test_missing_id(self):
		""" Gfycat URLs missing UIDs should fail """
		_task, _prog, _file = mock_handler_request(self.dir, 'https://gfycat.com/')
		res = gfycat.handle(_task, _prog)
		self.assertIs(res, False, "Invalid response after failed download!")
		self.assertFalse(_file.exists(), "A file was created for an invalid URL!")

	def test_fake_url(self):
		""" Imposter gfycat URLs should fail """
		_task, _prog, _file = mock_handler_request(self.dir, 'https://gfycat.com.fake.com/ripemadintermediateegret')
		res = gfycat.handle(_task, _prog)
		self.assertIs(res, False, "Invalid response after failed download!")
		self.assertFalse(_file.exists(), "A file was created for an invalid URL!")

	def test_direct_url(self):
		""" Direct gfycat URLs should work """
		_task, _prog, _file = mock_handler_request(self.dir, 'https://zippy.gfycat.com/DampAltruisticGangesdolphin.webm')
		res = gfycat.handle(_task, _prog)
		self.assertTrue(res, "gfycat webm download failed!")
		self.assertTrue(_file.exists(), "gfycat webm was not downloaded! %s" % res.failure_reason)
		self.assertIn('.webm', _file.relative(), "gfycat webm is missing extension!")

	def test_decorated(self):
		""" A Gfycat link with extra social string should work """
		_task, _prog, _file = mock_handler_request(self.dir, 'https://gfycat.com/ripemadintermediateegret-hi-bye-sad-nba')
		res = gfycat.handle(_task, _prog)
		self.assertTrue(res, "gfycat webm download failed!")
		self.assertTrue(_file.exists(), "gfycat webm was not downloaded! %s" % res.failure_reason)
		self.assertIn('.webm', _file.relative(), "gfycat webm is missing extension!")

