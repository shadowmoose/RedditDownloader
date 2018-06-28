from classes.sources import source
import classes.static.praw_wrapper as reddit


class UpvotedSaved(source.Source):
	def __init__(self):
		super().__init__(source_type='personal-upvoted-saved',
						 description="Submissions and Comments you've saved or upvoted.")
		self._elements = []

	def get_elements(self):
		for ele in reddit.my_liked_saved():
			if self.check_filters(ele):
				yield ele

	def get_settings(self):  # !cover
		return []

	def get_config_summary(self):  # !cover
		return "Scanning all your Upvoted/Saved Submissions & Comments."
