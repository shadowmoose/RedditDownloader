from sources import source
import reddit
import console


class UserPostsSource(source.Source):
	def __init__(self):
		super().__init__(source_type='user-posts-source', description="A User's Submission and/or Comment history")
		self._elements = []


	def get_elements(self):
		ret = []
		for re in reddit.user_posts(
				username    = self.data['user'],
				find_submissions= self.data['scan_submissions'],
				find_comments= self.data['scan_comments']):
			if self.check_filters(re):
				ret.append(re)
		return ret


	def setup_wizard(self):
		print('Setup wizard for %s' % self.get_alias())
		user = console.string('Name of the User to scan')
		if user is None:
			print('Aborting setup.')
			return False
		self.data['user'] = user

		choice = console.prompt_list('Would you like to scan their Submissions or Comments?', [
			('Only Submissions', 0), ('Only Comments', 1), ('Both Submissions & Comments', 2)
		])
		self.data['scan_submissions'] = (choice == 0 or choice == 2)
		self.data['scan_comments'] = (choice == 1 or choice == 2)
		feeds = ""
		if self.data['scan_comments']:
			feeds+="Comments"
		if self.data['scan_submissions']:
			if len(feeds) > 0:
				feeds+=" & "
			feeds+="Submissions"
		self.data['vanity'] = feeds
		return True


	def get_config_summary(self):
		return "Scanning User (%s)'s %s." % (self.data['user'], self.data['vanity'])