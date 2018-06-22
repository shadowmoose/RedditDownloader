from classes.sources import source
import classes.static.praw_wrapper as reddit


class TestPostProducer(source.Source):
	def __init__(self):
		super().__init__(source_type='test-source-producer', description="Random test posts - Don't use this one.")
		self.filters = []


	def get_elements(self):
		for p in reddit.frontpage_posts(
				order_by = 'top',
				limit    = 30,
				time     = 'all'):
			if self.check_filters(p):
				yield p #!cover
		for p in reddit.subreddit_posts(
				sub      = 'funny',
				order_by = 'controversial',
				limit    = 20,
				time     = 'week'):
			if self.check_filters(p):
				yield p #!cover
		for re in reddit.user_posts(
				username   = 'test_reddit_scraper',
				find_submissions= True,
				find_comments= True):
			if self.check_filters(re):
				yield re #!cover
		for ele in reddit.user_liked_saved('test_reddit_scraper', True, True):
			if self.check_filters(ele):
				yield ele #!cover
		for p in reddit.multi_reddit(# https://www.reddit.com/user/Lapper/m/depthhub/
				username    = 'Lapper',
				reddit_name = 'depthhub',
				order_by = 'new',
				limit    = 10,
				time     = 'all'):
			if self.check_filters(p):
				yield p #!cover


	def apply_filters(self, new_filters):
		"""  Sets the filters for this test source. """
		self.filters = new_filters


	def get_settings(self): #!cover
		return []


	def get_config_summary(self): #!cover
		return 'Downloading random, test Post data.'