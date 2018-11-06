from classes.filters import filter
from classes.static import stringutil


class UTCFilter(filter.Filter):
	def __init__(self):
		super().__init__(field='created_utc', description='The time this post/comment was created, in UTC. (#)')

	def _convert_imported_limit(self, val):
		"""  Overrides default to convert user-supplied string dates to timestamps.  """
		if not stringutil.is_numeric(val):
			stringutil.error("Error in UTC Filter: Expects time in a numeric UTC timestamp.")  # !cover
		return val
