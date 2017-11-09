from sources import source
import reddit



class UpvotedSaved(source.Source):
	def __init__(self):
		super().__init__(source_type='personal-upvoted-saved')
		self._elements = []


	def get_elements(self):
		return [ele for ele in reddit.my_liked_saved() if self.check_filters(ele)]# Use filters.


	def setup_wizard(self):
		print('Setup wizard for %s' % self.alias)
		print('This source requires no additional information.')