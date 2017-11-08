"""
	Filter class
	OVERIDES:
		init() !- To set the field value
		check() - If this Filter needs to use custom logic to check values
		parse_limit() - If the user-supplied limit value needs converting.
"""
import pkgutil
import filters
import os
import re

class Filter:

	def __init__(self, field, description):
		""" Creates a new Filter with the given field name/operator/limit. """
		self.field = field
		self.operator = None
		self.limit = None
		self.description = description
		self.operators = {'<':'.max', '>':'.min', '=':'', 're':'.regex'}


	def check(self, obj):
		"""  Checks the given object to verify if this Filter's field - within the object - is within parameters.
			Automatically casts numeric values if possible, then compares.
		"""
		if self.field not in obj:
			return True
		if self.operator == '<':
			return self.cast(obj[self.field]) < self.cast(self.limit)
		if self.operator == '>':
			return self.cast(obj[self.field]) > self.cast(self.limit)
		if self.operator == '=':
			return self.cast(obj[self.field]) == self.cast(self.limit)
		if self.operator == 're':
			pattern = re.compile(str(self.limit), re.IGNORECASE)
			if pattern.match(str(obj[self.field])):
				return True
			return False
		assert False # This should never happen.


	def cast(self, val):
		"""  Attempt to cast to number, or just return the original value.  """
		try:
			return float(val)
		except ValueError:
			return str(val)


	def parse_limit(self, val):
		""" Does nothing by default, exists to allow easy overriding to convert input limit values. """
		return val


	def from_obj(self, key, value):
		"""
			Expects key, value pair from Settings. Parses this setting into a Filter object.
			Returns False if this Filter doesn't match the given key.
		"""
		self.limit = self.parse_limit(value)
		return self._parse_str(key)


	def to_obj(self):
		""" Convert this source into a data model that can be saved/loaded from Settings. """
		return {self.field+self._lookup_operator(self.operator, True) : self.limit}


	def _parse_str(self, str_key):
		"""  Parses the given filter string into this filter, setting its values.  """
		if self.field not in str_key:
			return False
		op = None
		for k, v in self.operators.items():
			if v != '' and v in str_key.lower():
				op = k
		if '.' not in str_key:
			op = '='
		if self._lookup_operator(op):
			self.operator = op
		else:
			print('Unable to parse operator for Filter: %s' % self.field)
			return False
		return True


	def _lookup_operator(self, op, return_value=False):
		"""  Returns if this operator is a valid operator string or not. If set, returns mapped value. """
		if op in self.operators:
			if return_value:
				return self.operators[op]
			return True
		return False


	def __str__(self):
		return "filter: %s %s %s (%s)" % (self.field, self.operator, self.limit, self.description)



def get_filters(filter_dict=None):
	""" Get a list of all availale Filter objects.
		If passed a dict of {'field.operator':val} - as specified by the filter settings syntax -
			it will return loaded filters objects.
	"""
	#TODO:	Perhaps it would be simplest to generate a bunch of known fields in a loop (from generic Filter() objects)
	#TODO:	since the generic class works for almost every field in a Post/Comment by default.  - maybe generate defaults unless a custom overrides?
	pkg_path = os.path.dirname(filters.__file__)
	loaded = []
	used = []
	# Load packaged classes first, as they need to be treated specially in the event of custom data.
	for _,name,_ in pkgutil.iter_modules([pkg_path]):
		if '_filter' not in name:
			continue
		fi = __import__(name, fromlist=[''])
		for clazz in _module_classes(fi):
			if filter_dict:
				for k, v in filter_dict.items():
					cl = clazz()
					if cl.from_obj(k, v):
						loaded.append(cl)
						used.append(cl.field)
			else:
				cl = clazz()
				loaded.append(cl)
				used.append(cl.field)
	# Append default field filters, if not already handled by special one above.
	for k, v in get_filter_fields().items():
		if k in used:
			continue
		if filter_dict:
			for loaded_field, loaded_val in filter_dict.items():
				cl = Filter(field=k, description=v) # New filter for default values.
				if cl.from_obj(loaded_field, loaded_val):
					loaded.append(cl)
		else:
			cl = Filter(field=k, description=v) # New filter for default values.
			loaded.append(cl)

	return loaded


def _module_classes(module):
	"""  Pull the classes from the given module.  """
	md = module.__dict__
	return [
		md[c] for c in md if (
			isinstance(md[c], type) and md[c].__module__ == module.__name__
		)
	]

def get_filter_fields():
	""" Builds a list of acceptable fields to filter this Element by. """
	return {
		'link_count': 'The amount of links found for this element. (#)',
		'element_type': 'The type of element this is. (Post/Comment)',
		'title':  'The title of this post containing this element. (String)',
		'author': 'The author of this element. (String)',
		'body':  'The text in this element. Blank if a Post without selftext. (String)',
		'subreddit': 'The subreddit this element is from. (String)',
		'over_18': 'If this post is age-limited. (True/False)',
		'created_utc':'The timestamp, in UTC seconds, that this element was posted. (#)',
		'num_comments': 'The number of comments on this element. (#)',
		'score': 'The number of net upvotes on this element. (#)',
	}

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




if __name__ == '__main__':
	print('All available:')
	for f in get_filters():
		print(f)
	print()
	print("Loading...")

	test_post = {'created_utc':99, 'title':'Test Title'}
	all_filters = get_filters({
		'created_utc.min':10,
		'created_utc.max':100,
		'created_utc': 99,
		'created_utc.regex': '99',
		'title.regex':'Test'
	})
	print('Loaded Filters:')
	for f in all_filters:
		print('\t', f.to_obj())

	print('\nRunning checks on test:', test_post)
	for f in all_filters:
		print(f.check(test_post), '|', f)
	#TODO: Write a test for a large range of these, and compare the list get_filters returns to make sure they all load.