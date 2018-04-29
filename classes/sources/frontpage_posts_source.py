from classes.sources import source
import classes.reddit.reddit as reddit
from classes.util import console


class UserPostsSource(source.Source):
	def __init__(self):
		super().__init__(source_type='frontpage-posts-source', description="The submissions on your front page")
		self._elements = []


	def get_elements(self):
		for p in reddit.frontpage_posts(
				order_by = self.data['order'],
				limit    = self.data['limit'],
				time     = self.data['time']):
			if self.check_filters(p):
				yield p


	def setup_wizard(self):
		print('Setup wizard for %s' % self.get_alias())
		order = console.prompt_list(
			'How would you like to sort these Submissions?',
			[(r[0], r) for r in reddit.post_orders()]
		)
		self.data['order'] = order[0]
		self.data['time'] = 'all'
		if order[1]:
			self.data['time'] = console.prompt_list('Select a time span to filter by:', reddit.time_filters())
		self.data['limit'] = console.number('How many would you like to download? (0 for no limit)')
		return True


	def get_config_summary(self):
		lim = self.data['limit']
		if lim > 0:
			lim = 'first %s posts' % lim
		else:
			lim = ''
		return 'Downloading %s %s submissions from your front page, within "%s" time.' % (
			lim, self.data['order'], self.data['time']
		)