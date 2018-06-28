from classes.sources import source
import classes.static.praw_wrapper as reddit
from classes.static.settings import Setting


class UserPostsSource(source.Source):
	def __init__(self):
		super().__init__(source_type='frontpage-posts-source', description="The submissions on your front page.")
		self._elements = []

	def get_elements(self):
		for p in reddit.frontpage_posts(order_by=self.data['order'], limit=self.data['limit'], time=self.data['time']):
			if self.check_filters(p):
				yield p

	def get_settings(self):
		yield Setting('order', None, etype='str', desc='Order submissions by:', opts=reddit.post_orders())
		yield Setting('time', None, etype='str', desc='Select a time span to filter by:', opts=reddit.time_filters())
		yield Setting('limit', 0, etype='int', desc='How many would you like to download? (0 for no limit):',)

	def get_config_summary(self):
		lim = self.data['limit']
		if lim > 0:
			lim = 'first %s posts' % lim
		else:
			lim = ''
		return 'Downloading %s %s submissions from your front page, within "%s" time.' % (
			lim, self.data['order'], self.data['time']
		)
