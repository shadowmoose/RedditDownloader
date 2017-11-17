from sources import source
import reddit
import console


class MultiRedditSource(source.Source):
	def __init__(self):
		super().__init__(source_type='multi-reddit-source', description="The submissions from a user-curated MultiReddit.")
		self._elements = []


	def get_elements(self):
		ret = []
		for p in reddit.multi_reddit(
				username    = self.data['owner'],
				reddit_name = self.data['multi_name'],
				order_by = self.data['order'],
				limit    = self.data['limit'],
				time     = self.data['time']):
			if self.check_filters(p):
				ret.append(p)
		return ret


	def setup_wizard(self):
		print('Setup wizard for %s' % self.get_alias())
		while True:
			owner = console.string('Name of the redditor who curates the MultiReddit')
			if owner is None:
				print('Aborting setup.')
				return False
			if 'u/' in owner:
				print('Please only include the subreddit name, after the "/u/".')
				continue
			self.data['owner'] = owner
			break
		mr = console.string("Enter the name of this user's multireddit")
		if not mr:
			print("Setup canceled.")
			return False
		self.data['multi_name'] = mr

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
		return 'Downloading %s %s submissions from User  %s\'s multireddit "%s", within "%s" time.' % (
			lim, self.data['order'], self.data['owner'], self.data['multi_name'], self.data['time']
		)