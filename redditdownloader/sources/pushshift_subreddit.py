from sources import source
from psaw import PushshiftAPI
from static.settings import Setting
from processing.wrappers.redditelement import RedditElement


class PushShiftSubmissionSource(source.Source):
	def __init__(self):
		super().__init__(source_type='pushshift-submission-source', description="PushShift: The (possibly unlimited) submissions in one or more subreddits.")

	def get_elements(self):
		ps = PushshiftAPI()
		for sub in self.data['subreddit'].split(','):
			sub = sub.replace('/r/', '', 1).strip()
			_params = {'subreddit': sub}
			if self.data['limit']:
				_params['limit'] = self.data['limit']
			for post in ps.search_submissions(**_params):
				p = RedditElement(post)
				if self.check_filters(p):
					yield p

	def get_settings(self):
		yield Setting('subreddit', '', etype='str', desc='Name of the desired subreddit(s), separated by commas:')
		yield Setting('limit', 1000, etype='int', desc='How many would you like to download? (0 for no limit):')

	def get_config_summary(self):
		lim = self.data['limit']
		if lim > 0:
			lim = 'the first %s' % lim
		else:
			lim = 'all'
		return 'Downloading %s submissions from subreddit(s) "%s".' % (
			lim, self.data['subreddit']
		)
