import static.praw_wrapper as pw
import static.settings as settings
from processing.wrappers.redditelement import RedditElement
from tests.mock import EnvironmentTest


class PrawWrapperTest(EnvironmentTest):
	env = 'rmd_version_4'

	def setUp(self):
		settings.load(self.settings_file)

	def test_load_comment(self):
		""" Load Comment directly by ID """
		com = pw.get_comment(t1_id='t1_dxz6n80')
		re = RedditElement(com)
		vals = {
			"_urls": ['https://stackoverflow.com/a/23709194'],
			"type": 'Comment',
			"id": 't1_dxz6n80',
			"title": 'Reddit Media Downloader is now Threaded - Scrape all the subreddits, *much* faster now.',
			"author": 'theshadowmoose',
			"parent": 't3_8ewkx2',
			"subreddit": 'DataHoarder',
			"over_18": False,
			"created_utc": 1524705293.0,
			"link_count": 1,
			"source_alias": None,
		}
		for k, v in vals.items():
			self.assertEqual(getattr(re, k), v, msg='%s was not properly set in Comment!' % k.title())

	def test_load_submission(self):
		""" Load submission directly by ID """
		p = pw.get_submission(t3_id='t3_6es0u8')
		re = RedditElement(p)
		self.assertEqual(re.author, 'theshadowmoose', msg='Submission has invalid Author!')
		self.assertEqual(re.title, 'Test Direct Link', msg='Submission has invalid Title!')

	def test_frontpage_load(self):
		""" Load frontpage Submissions """
		posts = [p for p in pw.frontpage_posts(limit=3)]
		self.assertEqual(len(posts), 3, msg="PRAW found the wrong number of posts.")

	def test_liked_saved(self):
		""" Load Liked/Saved Posts """
		cnt = 0
		for p in pw.my_liked_saved():
			cnt += 1
			self.assertTrue(p, msg='Found invalid Post!')
		self.assertGreater(cnt, 0, msg="Found no Liked/Saved Posts!")

	def test_subreddit_submissions(self):
		""" Load submissions from a subreddit """
		self.assertGreater(len([p for p in pw.subreddit_posts('shadow_test_sub', limit=5)]), 3, msg='Loaded too few Posts.')

	def test_user_posts(self):
		""" Load test user posts """
		posts = [p for p in pw.user_posts('test_reddit_scraper', find_comments=True, find_submissions=True)]
		for p in posts:
			self.assertEqual(p.author, 'test_reddit_scraper', msg='Invalid Post author!')
