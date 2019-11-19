from sources import source
from psaw import PushshiftAPI
from static.settings import Setting
from processing.wrappers.redditelement import RedditElement


class PushShiftSearchSource(source.Source):
	def __init__(self):
		super().__init__(source_type='pushshift-search-source', description="PushShift: The results of a Submission search.")

	def get_elements(self):
		ps = PushshiftAPI()
		term = self.data['search_term']
		sub_list = self.data['subreddits'] or None
		subs = sub_list.split(',') if sub_list else [None]
		for sub in subs:
			if sub:
				sub = sub.strip()
			gen = ps.search_submissions(q=term, subreddit=sub, limit=self.data['limit'])
			for post in gen:
				p = RedditElement(post)
				if self.check_filters(p):
					yield p

	def get_settings(self):
		yield Setting('search_term', '', etype='str', desc='The term to search for:')
		yield Setting('subreddits', '', etype='str', desc='Optionally limit the search to specific subreddit(s), separated by commas:')
		yield Setting('limit', 1000, etype='int', desc='How many would you like to download per-subreddit? (0 for no limit):')

	def get_config_summary(self):
		lim = self.data['limit']
		if lim > 0:
			lim = 'the first %s' % lim
		else:
			lim = 'all'
		return 'Downloading %s search results from subreddit(s) "%s".' % (
			lim, self.data['subreddits']
		)

