import unittest
from processing.wrappers import ProgressManifest, DownloaderProgress, LoaderProgress
import json


class WrapperInitTest(unittest.TestCase):
	def test_progress_json(self):
		""" Make sure the JSON encoding isn't broken. """
		progg = ProgressManifest(
			downloaders=[DownloaderProgress(), DownloaderProgress()],
			loader=LoaderProgress(),
			deduplication=True,
			running=False
		)
		self.assertIsNotNone(json.dumps(progg.to_obj()))

