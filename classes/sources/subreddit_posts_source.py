from sources import source
import reddit
import console


class UserPostsSource(source.Source):
	def __init__(self):
		super().__init__(source_type='subreddit-posts-source', description="The submissions in a given subreddit")
		self._elements = []


	def get_elements(self):
		ret = []
		for p in reddit.subreddit_posts(
				sub      = self.data['subreddit'],
				order_by = self.data['order'],
				limit    = self.data['limit'],
				time     = self.data['time']):
			if self.check_filters(p):
				ret.append(p)
		return ret


	def setup_wizard(self):
		print('Setup wizard for %s' % self.get_alias())
		while True:
			sub = console.string('Name of the subreddit to scan')
			if sub is None:
				print('Aborting setup.')
				return False
			if 'r/' in sub:
				print('Please only include the subreddit name, after the "/r/".')
				continue
			self.data['subreddit'] = sub
			break
		print("Selected: %s" % sub)
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
		return 'Downloading %s %s submissions from subreddit "%s", within "%s" time.' % (
			lim, self.data['order'], self.data['subreddit'], self.data['time']
		)