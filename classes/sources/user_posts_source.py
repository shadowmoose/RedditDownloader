from sources import source
import reddit
import console


class UserPostsSource(source.Source):
	def __init__(self):
		super().__init__(source_type='user-posts-source', description="A User's Post and/or Comment history")
		self._elements = []


	def get_elements(self):
		return []# TODO: Set this bit up.


	def setup_wizard(self):
		print('Setup wizard for %s' % self.get_alias())
		user = console.string('Name of the User to scan')
		if user is None:
			print('Aborting setup.')
			return False
		self.data['user'] = user

		choice = console.prompt_list('Would you like to scan their Posts or Comments?', [
			('Only Posts', 0), ('Only Comments', 1), ('Both Posts & Comments', 2)
		])
		self.data['scan_posts'] = (choice == 0 or choice == 2)
		self.data['scan_comments'] = (choice == 1 or choice == 2)
		return True


	def get_config_summary(self):
		feeds = ""
		if self.data['scan_comments']:
			feeds+="Comments"
		if self.data['scan_posts']:
			if len(feeds) > 0:
				feeds+="&"
			feeds+="Posts"
		return "Scanning User (%s)'s %s." % (self.data['user'], feeds)