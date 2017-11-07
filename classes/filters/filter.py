"""
	Generic Filter class, all filters should override the init (to hardcode fields)
"""

class Filter:
	def __init__(self, field, operator, limit):
		""" Creates a new Filter with the given field name/operator/limit. """
		self.field = field #
		self.operator = operator
		self.limit = limit
		self.name = self.field # User-friendly field name
		assert self._validate_operator(self.operator)


	def check(self, obj):
		"""  Checks the given object to verify if this Filter's field - within the object - is within parameters.  """
		if self.field not in obj:
			return False
		if self.operator == '<':
			return obj[self.field] < self.limit
		if self.operator == '>':
			return obj[self.field] > self.limit
		if self.operator == '=':
			return obj[self.field] == self.limit
		assert False # This should never happen.


	def load_obj(self, key, value):
		"""
			Expects key, value pair from Settings. Parses this setting into a Filter object.
			Returns False if this Filter doesn't match the given key.
		"""
		self.limit = value
		return self._parse_str(key)


	def _parse_str(self, str_key):
		"""  Parses the given filter string into this filter, setting its values.  """
		if self.name not in str_key:
			return False
		op = None
		if '.min' in str_key:
			op = '>'
		elif '.max' in str_key:
			op = '<'
		elif '.' not in str_key:
			op = '='
		if self._validate_operator(op):
			self.operator = op
		else:
			print('Unable to parse operator for Filter: %s' % self.name)
			return False
		return True


	def _validate_operator(self, op):
		"""  Returns if this operator is a valid operator string or not.  """
		if op in ['>', '<', '=']:
			return True
		return False


	def __str__(self):
		return "filter: %s %s %s" % (self.field, self.operator, self.limit)

"""
"filters":[
	{
		"created_utc.min": 0,
		"created_utc.max": 0,
		"score.min": 0,
		"author": "shadowmoose"
	}
]
"""