from classes.sources import source
import classes.static.praw_wrapper as reddit
from classes.static.settings import Setting


class SubredditPostsSource(source.Source):
	def __init__(self):
		super().__init__(source_type='subreddit-posts-source', description="The submissions in one or more subreddits")
		self._elements = []

	def get_elements(self):
		for sub in self.data['subreddit'].split(','):
			for p in reddit.subreddit_posts(
					sub      = sub.strip(),
					order_by = self.data['order'],
					limit    = self.data['limit'],
					time     = self.data['time']):
				if self.check_filters(p):
					yield p

	def get_settings(self):
		yield Setting('subreddit', '', etype='str', desc='Name of the desired subreddit(s), separated by commas:')
		yield Setting('order', None, etype='str', desc='Order submissions by:', opts=reddit.post_orders())
		yield Setting('time', None, etype='str', desc='Select a time span to filter by:', opts=reddit.time_filters())
		yield Setting('limit', 0, etype='int', desc='How many would you like to download? (0 for no limit):')

	def get_config_summary(self):
		lim = self.data['limit']
		if lim > 0:
			lim = 'first %s posts' % lim
		else:
			lim = ''
		return 'Downloading %s %s submissions from subreddit "%s", within "%s" time.' % (
			lim, self.data['order'], self.data['subreddit'], self.data['time']
		)
