from sources import source
from psaw import PushshiftAPI
from static.settings import Setting
from processing.wrappers.redditelement import RedditElement


class PushShiftUserSourceSource(source.Source):
	def __init__(self):
		super().__init__(source_type='pushshift-user-source', description="PushShift: The (possibly unlimited) posts made by a User.")

	def get_elements(self):
		ps = PushshiftAPI()
		for user in self.data['users'].split(','):
			user = user.replace('/u/', '', 1).strip()
			_params = {'author': user}
			if self.data['limit']:
				_params['limit'] = self.data['limit']
			if self.data['scan_submissions']:
				for post in ps.search_submissions(**_params):
					p = RedditElement(post)
					if self.check_filters(p):
						yield p
			if self.data['scan_comments']:
				for post in ps.search_comments(**_params):
					sub = list(ps.search_submissions(ids=post.link_id.replace('t3_', '', 1), limit=1))[0]
					p = RedditElement(post, ext_submission_obj=sub)
					if self.check_filters(p):
						yield p

	def get_settings(self):
		yield Setting('users', '', etype='str', desc='Name of the desired user account(s), separated by commas:')
		yield Setting('limit', 1000, etype='int', desc='How many would you like to download from each? (0 for no limit):')
		yield Setting('scan_comments', False, etype='bool', desc='Scan their comments (very slow)?')
		yield Setting('scan_submissions', True, etype='bool', desc='Scan their submissions?')

	def get_config_summary(self):
		lim = self.data['limit']
		if lim > 0:
			lim = 'the first %s' % lim
		else:
			lim = 'all'
		return 'Downloading %s posts from user(s) "%s".' % (
			lim, self.data['users']
		)

