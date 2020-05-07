import re
from psaw import PushshiftAPI
from sources.source import Source
from processing.wrappers.redditelement import RedditElement


class DirectURLSource(Source):
	def __init__(self, url=None):
		super().__init__(source_type='direct-url-source', description="Entered a URL on the command line, for direct downloading.")
		self.data['url'] = url

	def get_elements(self):
		url = self.data['url']
		submission = re.search(r'\/comments\/([a-zA-Z0-9]+)\/?', url)
		comment = re.search(r'\/comments\/.+?\/.+?\/([a-zA-Z0-9]+)\/?', url)
		ps = PushshiftAPI()

		if comment:
			for post in ps.search_comments(ids=[comment.group(1)]):
				parents = list(ps.search_submissions(ids=post.link_id.replace('t3_', '', 1), limit=1))
				if not len(parents):
					raise AssertionError("PushShift Warning: Unable to locate direct parent Submission:", post.link_id)
				submission = parents[0]
				p = RedditElement(post, ext_submission_obj=submission)
				if self.check_filters(p):
					yield p
		elif submission:
			for post in ps.search_submissions(ids=[submission.group(1).replace('t3_', '', 1)], limit=1):
				p = RedditElement(post)
				if self.check_filters(p):
					yield p
		else:
			raise TypeError('Invalid Reddit URL provided! "%s"' % url)

	def get_config_summary(self):
		return self.data
