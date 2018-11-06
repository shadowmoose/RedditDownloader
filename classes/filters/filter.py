"""
	Filter class and static methods to access all available filters.
"""

import re
from classes import filters


class Filter:
	"""
	The generic Filter class. Also used as the base for any custom filters.
	Filters are used by Sources to weed out RedditElements the user doesn't want.
	OVERRIDES:
		init() !- To set the field value
		check() - If this Filter needs to use custom logic to check values
		_convert_imported_limit() - If the user-supplied limit value needs converting.
	"""
	def __init__(self, field, description):
		""" Creates a new Filter with the given field name/operator/limit. """
		self.field = field
		self.operator = None
		self._limit = None
		self.description = description
		self.accepts_operator = True

	def set_operator(self, op):  # !cover
		""" Sets this Filter's Operator. """
		if isinstance(op, str):
			op = self._get_operator_from_str(op)
		if self._validate_operator(op):
			self.operator = op
			return True
		raise KeyError('Attempted to set invalid Filter operator:', op)

	def set_limit(self, limit):
		""" Sets the limit of this Filter. Autocasts as needed. """
		self._limit = self._convert_imported_limit(self._cast(limit))

	def get_limit(self):
		return self._limit

	def get_description(self):
		return self.description

	def check(self, obj):
		"""  Checks the given object to verify if this Filter's field - within the object - is within parameters.
			Automatically casts numeric values if possible, then compares.
		"""
		if not hasattr(obj, self.field):
			raise Exception('No field: %s' % self.field)  # !cover
		val = self._cast(getattr(obj, self.field))
		lim = self.get_limit()
		if isinstance(val, str) or isinstance(lim, str):  # Case doesn't matter for the basic comparisons.
			val = str(val).lower()
			lim = str(lim).lower()
		if self.operator == filters.Operators.MAXIMUM:
			return val <= lim
		if self.operator == filters.Operators.MINIMUM:
			return val >= lim
		if self.operator == filters.Operators.EQUALS:
			return val == lim
		if self.operator == filters.Operators.MATCH:
			regexp = re.compile(str(self.get_limit()), re.IGNORECASE)
			if regexp.search(str(val)):
				return True
			return False
		raise Exception("Invalid comparator for Filter! %s" % self.operator)  # !cover

	def _cast(self, val):
		"""  Attempt to cast to integer, or just return the value as a string.  """
		try:
			return int(float(val))
		except ValueError:
			return str(val)

	def _convert_imported_limit(self, val):
		""" Returns unchanged val by default.
			Exists to allow easy overriding to convert input limit values.
			Return None to signify invalid value, and cancel from_obj() build.
		"""
		return val

	def from_obj(self, key, value):
		"""
			Expects key, value pair from Settings. Parses this setting into a Filter object.
			Returns False if this Filter doesn't match the given key.
		"""
		ret = self._parse_str(key)
		if not ret:
			return False
		conv = self._convert_imported_limit(value)
		if conv is None:
			return False
		self.set_limit(conv)
		return ret

	def to_js_obj(self):
		""" Build an object that represents this Filter. Used by WebUI. """
		return {
			'field': self.field,
			'operator': self.operator.value if self.operator else None,
			'accepts_operator': self.accepts_operator,
			'limit': self._limit,
			'description': self.description
		}

	def to_keyval(self):
		""" Convert this source into a data model that can be saved/loaded from Settings.
			Returns: key, val -> This represents the way this is stored within the "Filters" JSON Object.
		"""
		op = self._validate_operator(self.operator, True)
		if not op:
			op = ''
		return self.field+op, self._limit

	def _parse_str(self, str_key):
		"""  Parses the given filter string into this filter, setting its values.  """
		if self.field not in str_key:
			return False
		op = self._get_operator_from_str(str_key)
		if '.' not in str_key:
			op = filters.Operators.EQUALS  # !cover
		if self._validate_operator(op):
			self.operator = op
		else:
			raise Exception('Unable to parse operator for Filter: %s' % self.field)  # !cover
		return True

	def _validate_operator(self, op, return_value=False):
		"""  Returns if this operator is a valid operator string or not. If set, returns mapped value. """
		if op in filters.Operators:
			if return_value:
				return op.value
			return True
		return False

	def _get_operator_from_str(self, val):
		""" Attempts a (really generous) search to match the given string to a valid Operator. """
		for k in filters.Operators:
			if k.value.lower().strip() in val.lower().strip():
				return k

	def __str__(self):  # !cover
		lim = self._limit
		if isinstance(lim, str):
			lim = '"%s"' % lim
		if self.operator is None or lim is None:
			return "Filter: %s (%s)" % (self.field, self.description)
		return "Filter: %s %s %s (%s)" % (
			self.field,
			self.operator.value.replace('.', ''),
			lim,
			self.description
		)
