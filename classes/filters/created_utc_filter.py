from filters import filter
import dateutil.parser


class UTCFilter(filter.Filter):
	def __init__(self):
		super().__init__(field='created_utc', description='The time this post/comment was created, in UTC.')

	def _convert_imported_limit(self, val):
		"""  Overrides default to convert user-supplied string dates to timestamps.  """
		if self.is_number(val):
			return val
		try:
			date = dateutil.parser.parse(str(val))
			print('Normalized date to: ', date.timestamp())
			return date.timestamp()
		except ValueError:
			import stringutil
			stringutil.error('Cannot normalize given date! Try re-entering as a unix timestamp.')
		return val

	def is_number(self, s):
		try:
			float(s)
			return True
		except ValueError:
			return False