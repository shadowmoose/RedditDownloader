import unittest
from psaw import PushshiftAPI
from processing.wrappers.redditelement import RedditElement


class PSAWTest(unittest.TestCase):
	def test_gallery(self):
		""" Should load all gallery images """
		ps = PushshiftAPI()
		post, = ps.search_submissions(limit=1, ids=['t3_hrrh23'])
		re = RedditElement(post)
		self.assertEqual(len(re.get_urls()), 3, msg='Got incorrect image count from PSAW gallery submission!')
		for url in re.get_urls():
			self.assertIn('https', url, msg='Failed to extract valid gallery URL: %s' % url)

	def test_missing_author(self):
		""" Really old posts should still work without old author data """
		ps = PushshiftAPI()
		post, = ps.search_submissions(limit=1, ids=['t3_otfrw'])
		re = RedditElement(post)
		self.assertEqual(re.author, 'Deleted')
