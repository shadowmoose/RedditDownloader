from filters import filter

class UTCFilter(filter.Filter):
	def __init__(self):
		super().__init__(field='created_utc', description='The time this post/comment was created, in UTC.')