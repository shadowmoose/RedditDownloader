from classes.sources import source
import classes.reddit.praw_wrapper as reddit
from classes.util.settings import Setting

class UserUpvotedSaved(source.Source):
	def __init__(self):
		super().__init__(source_type='user-upvoted-saved', description="Submissions and Comments a Redditor has Upvoted or Saved.")
		self._elements = []


	def get_elements(self):
		dat = self.data
		for ele in reddit.user_liked_saved(dat['user'], dat['scan_upvoted'], dat['scan_saved'], dat['scan_sub']):
			if self.check_filters(ele):
				yield ele


	def get_settings(self):
		yield Setting('user', '', etype='str', desc='Target username:')
		yield Setting('scan_upvoted', False, etype='bool', desc='Scan the posts they\'ve upvoted?')
		yield Setting('scan_saved', False, etype='bool', desc='Scan the posts they\'ve saved?')
		yield Setting('scan_sub', '', etype='str', desc='Scan a specific Subreddit (leave blank for all):')


	def get_config_summary(self):
		feeds = ""
		if self.data['scan_upvoted']:
			feeds+="Upvoted"
		if self.data['scan_saved']:
			if len(feeds) > 0:
				feeds+=" & "
			feeds+="Saved"
		return 'Scanning all the Posts the Redditor "%s" has %s.' % (self.data['user'], feeds)
