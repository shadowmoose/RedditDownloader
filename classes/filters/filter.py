"""
	Generic Filter class, all filters should override the init (to hardcode fields)
"""

class Filter:
	def __init__(self, field, operator, limit):
		""" Creates a new Filter with the given field name/operator/limit. """
		self.name = 'Blank Filter'
		self.field = field
		self.operator = operator
		self.limit = limit
		assert self.operator in ['gt', 'lt', 'eq']


	def check(self, obj):
		""" Checks the given object to verify if this Filter's field - within the object - is within parameters. """
		if self.field not in obj:
			return False
		if self.operator == 'lt':
			return obj[self.field] < self.limit
		if self.operator == 'gt':
			return obj[self.field] > self.limit
		if self.operator == 'eq':
			return obj[self.field] == self.limit
		assert False # This should never happen.


	def __str__(self):
		return "filter: %s %s %s" % (self.field, self.operator, self.limit)