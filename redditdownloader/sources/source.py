"""
	Generic Source class, all actual sources should override this.
"""
import filters as filters


class Source:
	"""
	Source objects have simply:

	OVERRIDES:
		init() !- To set type
		get_elements() !- To return the values from this Source
		get_settings() !- Returns a list/iterator/etc of Settings objects required for this Source.
		get_config_summary() !- The function to return a user-friendly setup status.
	"""
	def __init__(self, source_type, description):
		"""
		The Source object, the core provider of RedditElements to the rest of the system.

		:param source_type: The ID of which Source object to load as
		:param description: The description to show the User.
		"""
		self.type = source_type
		self.description = description
		self._alias = self.type
		self.filters = []
		self.data = {}
		for _s in self.get_settings():
			self.data[_s.name] = _s.val()

	def get_elements(self):
		"""  Tells this Source to build and return a generator for RedditElements. """
		pass

	def get_config_summary(self):
		""" Override this method to print out a user-friendly string descriping this Source's current configuration. """
		return "No status"

	def get_settings(self):
		"""  Fetch an iterable of Settings() objects, which are needed to configure this source. """
		return []

	def available_filters(self):
		""" Returns a list of the available filters this Source can listen to. """
		return filters.get_filters()

	def set_alias(self, alias):
		""" Set the alias of this Source. """
		self._alias = alias

	def get_alias(self):
		""" Accessor for this Source's alias. """
		return self._alias

	def check_filters(self, ele):
		""" Checks if the given RedditElement can pass this Source's filters. """
		for fi in self.filters:
			if not fi.check(ele):
				return False
		return True

	def get_settings_obj(self):
		""" Builds an object of the Settings this Source needs. For WebUI use. """
		obj = []
		for _s in self.get_settings():
			obj.append(_s.to_obj())
		return obj

	def insert_data(self, key, val):
		self.data[key] = val

	def get_filters(self):
		return self.filters

	def remove_filter(self, rem_filter):
		self.filters.remove(rem_filter)

	def add_filter(self, new_filter):
		self.filters.append(new_filter)

	def from_obj(self, obj):
		"""
		Build this Source from the data model loaded.
		Returns False if this Source doesn't match the given object. If True, this Source has been initialized.
		"""
		if self.type != obj['type']:
			return False
		for k, v in obj['data'].items():
			self.data[k] = v
		self._alias = obj['alias']
		self._load_filters(obj)
		return True

	def to_obj(self, for_webui=False):
		"""  Convert this Source into a data model that can be output to the Settings file.  """
		out = {'type': self.type, 'filters': {}, 'data': self.data, 'alias': self._alias}
		for fi in self.get_filters():
			k, v = fi.to_keyval()
			out['filters'][k] = v
		if for_webui:
			out['settings'] = self.get_settings_obj()
			out['description'] = self.description
			out['filters'] = []
			for fi in self.get_filters():
				out['filters'].append(fi.to_js_obj())
		return out

	def _load_filters(self, data):
		""" Builds the list of filters this object needs. """
		if 'filters' not in data:
			return False  # !cover
		self.filters = filters.get_filters(data['filters'])

	def __repr__(self):
		return "(Source: %s :: %s)" % (self.type, self.get_config_summary())
