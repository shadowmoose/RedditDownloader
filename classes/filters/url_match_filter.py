from classes.filters import filter
import re

class URLFilter(filter.Filter):
	def __init__(self):
		super().__init__(field='url_pattern', description='Individual URLs in each Post, matching a regex pattern.')
		self.operator = filter.Operators.MATCH
		self.accepts_operator = False
		self._reg = None


	def check(self, obj):
		if not self._reg:
			self._reg = re.compile(str(self.get_limit()), re.IGNORECASE)
		urls = obj.get_urls()
		for ur in urls:
			if not self._reg.search( str(ur).lower()):
				obj.remove_url(ur)
		return len(obj.get_urls()) > 0