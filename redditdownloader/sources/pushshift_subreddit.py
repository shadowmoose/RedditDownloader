from sources import source
from psaw import PushshiftAPI
from static.settings import Setting
from processing.wrappers.redditelement import RedditElement
import time


class PushShiftSubmissionSource(source.Source):
	def __init__(self):
		super().__init__(source_type='pushshift-submission-source', description="PushShift: The (possibly unlimited) submissions in one or more subreddits.")

	def get_elements(self):
		ps = PushshiftAPI()
		for sub in self.data['subreddit'].split(','):
			sub = sub.replace('/r/', '', 1).strip()
			_params = {'subreddit': sub, 'sort_type': self.data['sort_by'], 'after': self.convert_offset()}
			if self.data['limit']:
				_params['limit'] = self.data['limit']
			if 'desc' in self.data['sort_order'].lower():
				_params['sort'] = 'desc'
			else:
				_params['sort'] = 'asc'
			print(_params)
			for post in ps.search_submissions(**_params):
				p = RedditElement(post)
				if self.check_filters(p):
					yield p

	def get_settings(self):
		yield Setting('subreddit', '', etype='str', desc='Name of the desired subreddit(s), separated by commas:')
		yield Setting('limit', 1000, etype='int', desc='How many would you like to download? (0 for no limit):')
		yield Setting("time", 'All Time', desc='Select a time span to filter by:', etype="str", opts=[('All Time', 'All posts ever made'), ('Day', 'Posts with the last 24hrs'), ('Week', 'Posts within the last 7 days'), ('Month', "Posts within the last 31 days"), ('Year', 'Posts within the last 265 days')])
		yield Setting("sort_by", 'score', desc="Sort results by:", etype="str", opts=[('score', 'Sort by highest score'), ('created_utc', 'The datetime the Submission was created')])
		yield Setting("sort_order", 'Descending', desc="Sort order:", etype="str", opts=[('Descending', 'Descending order'), ('Ascending', "Ascending order")])

	def get_config_summary(self):
		lim = self.data['limit']
		if lim > 0:
			lim = 'the first %s' % lim
		else:
			lim = 'all'
		return 'Downloading %s submissions from subreddit(s) "%s".' % (
			lim, self.data['subreddit']
		)

	def convert_offset(self):
		current_time = int(time.time())
		off = self.data['time'].lower()
		day = 24*60*60
		if 'all' in off:
			return 0
		if off == 'day':
			return current_time - day
		if off == 'week':
			return current_time - (day*7)
		if off == 'month':
			return current_time - (day*31)
		if off == 'year':
			return current_time - (day*365)
		raise Exception("Unhandled time span!")
