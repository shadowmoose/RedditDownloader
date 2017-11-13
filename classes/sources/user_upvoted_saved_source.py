from sources import source
import reddit

class UserUpvotedSaved(source.Source):
	def __init__(self):
		super().__init__(source_type='user-upvoted-saved', description="Submissions and Comments a Redditor has Upvoted or Saved")
		self._elements = []


	def get_elements(self):
		gen = reddit.user_liked_saved(self.data['user'], self.data['scan_upvoted'], self.data['scan_saved'])
		return [ele for ele in gen if self.check_filters(ele)]# Use filters.


	def setup_wizard(self):
		print('Setup wizard for %s' % self.get_alias())
		import console
		user = console.string('Name of the User to scan')
		if user is None:
			print('Aborting setup.')
			return False
		self.data['user'] = user

		choice = console.prompt_list('Would you like to scan the Posts they\'ve Upvoted or Saved?', [
			('Only Upvoted Posts', 0), ('Only Saved Posts', 1), ('Both Upvoted & Saved Posts', 2)
		])
		self.data['scan_upvoted'] = (choice == 0 or choice == 2)
		self.data['scan_saved'] = (choice == 1 or choice == 2)
		feeds = ""
		if self.data['scan_upvoted']:
			feeds+="Upvoted"
		if self.data['scan_saved']:
			if len(feeds) > 0:
				feeds+=" & "
			feeds+="Saved"
		self.data['vanity'] = feeds
		return True


	def get_config_summary(self):
		return 'Scanning all the Posts the Redditor "%s" has %s.' % (self.data['user'], self.data['vanity'])