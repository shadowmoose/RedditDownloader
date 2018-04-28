from sources import source
import reddit.reddit as reddit



class UpvotedSaved(source.Source):
	def __init__(self):
		super().__init__(source_type='personal-upvoted-saved', description="Submissions and Comments you've saved or upvoted.")
		self._elements = []


	def get_elements(self):
		for ele in reddit.my_liked_saved():
			if self.check_filters(ele):
				yield ele


	def setup_wizard(self): #!cover
		print('Setup wizard for %s' % self.get_alias())
		print('This source requires no additional information.')
		return True


	def get_config_summary(self): #!cover
		return "Scanning all your Upvoted/Saved Submissions & Comments."