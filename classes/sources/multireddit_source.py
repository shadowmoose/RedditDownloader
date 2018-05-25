from classes.sources import source
import classes.reddit.reddit as reddit
from classes.util.settings import Setting

class MultiRedditSource(source.Source):
	def __init__(self):
		super().__init__(source_type='multi-reddit-source', description="The submissions from a user-curated MultiReddit.")
		self._elements = []


	def get_elements(self):
		for p in reddit.multi_reddit(
				username    = self.data['owner'],
				reddit_name = self.data['multi_name'],
				order_by = self.data['order'],
				limit    = self.data['limit'],
				time     = self.data['time']):
			if self.check_filters(p):
				yield p


	def get_settings(self):
		yield Setting('owner', '', etype='str', desc='Username of this multireddit owner:')
		yield Setting('multi_name', '', etype='str', desc='Name of this user\'s multireddit:')
		yield Setting('order', None, etype='str', desc='Order submissions by:', opts=reddit.post_orders())
		yield Setting('time', None, etype='str', desc='Select a time span to filter by:', opts=reddit.time_filters())
		yield Setting('limit', 0, etype='int', desc='How many would you like to download? (0 for no limit):')


	def get_config_summary(self):
		lim = self.data['limit']
		if lim > 0:
			lim = 'first %s posts' % lim
		else:
			lim = ''
		return 'Downloading %s %s submissions from User  %s\'s multireddit "%s", within "%s" time.' % (
			lim, self.data['order'], self.data['owner'], self.data['multi_name'], self.data['time']
		)