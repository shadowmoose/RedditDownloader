from sources import source
import static.praw_wrapper as reddit
from static.settings import Setting


class UserPostsSource(source.Source):
	def __init__(self):
		super().__init__(source_type='user-posts-source', description="A User's Submission and/or Comment history.")
		self._elements = []

	def get_elements(self):
		for re in reddit.user_posts(
				username=self.data['user'],
				find_submissions=self.data['scan_submissions'],
				find_comments=self.data['scan_comments']):
			if self.check_filters(re):
				yield re

	def get_settings(self):
		yield Setting('user', '', etype='str', desc='Target username:')
		yield Setting('scan_comments', False, etype='bool', desc='Scan their comments?')
		yield Setting('scan_submissions', False, etype='bool', desc='Scan their submissions?')

	def get_config_summary(self):
		feeds = ""
		if self.data['scan_comments']:
			feeds += "Comments"
		if self.data['scan_submissions']:
			if len(feeds) > 0:
				feeds += " & "
			feeds += "Submissions"
		return "Scanning User (%s)'s %s." % (self.data['user'], feeds)
