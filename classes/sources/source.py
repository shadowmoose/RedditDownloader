"""
	Generic Source class, all actual sources should override this.
"""
from classes.filters import filter
from classes import sources


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

	def get_elements(self):  # !cover
		"""  Tells this Source to build and return a generator for RedditElements. """
		pass

	def get_config_summary(self):  # !cover
		""" Override this method to print out a user-friendly string descriping this Source's current configuration. """
		return "No status"

	def get_settings(self):  # !cover
		"""  Make this Souce object prompt the user for the information it needs to retrieve data.
			Returns if the Source was properly set up or not.
		"""
		return []

	def available_filters(self):  # !cover
		""" Returns a list of the available filters this Source can listen to. """
		return filter.get_filters()

	def set_alias(self, alias):  # !cover
		""" Set the alias of this Source. """
		self._alias = alias

	def get_alias(self):  # !cover
		""" Accessor for this Source's alias. """
		return self._alias

	def check_filters(self, ele):  # !cover
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

	def get_filters(self):  # !cover
		return self.filters

	def remove_filter(self, rem_filter):  # !cover
		self.filters.remove(rem_filter)

	def add_filter(self, new_filter):  # !cover
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

	def to_obj(self, for_webui=False):  # !cover
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
		self.filters = filter.get_filters(data['filters'])


def get_sources(source_list=None):
	"""
	Get a list of all availale Sources.

	Expects that source_list is the direct array of Sources loaded from settings.
	"""
	import pkgutil
	import os
	pkg_path = os.path.dirname(sources.__file__)
	loaded = []
	for _, name, _ in pkgutil.iter_modules([pkg_path]):
		if '_source' not in name:
			continue
		fi = __import__('classes.sources.%s' % name, fromlist=[''])
		for clazz in _module_classes(fi):
			if source_list is not None:
				for obj in source_list:
					cl = clazz()  # build the class.
					if cl.from_obj(obj):  # if the class accepts this data.
						loaded.append(cl)
			else:  # !cover
				cl = clazz()
				loaded.append(cl)
	return loaded


def _module_classes(module_trg):
	"""  Pull the classes from the given module.  """
	md = module_trg.__dict__
	return [
		md[c] for c in md if (
			isinstance(md[c], type) and md[c].__module__ == module_trg.__name__
		)
	]


if __name__ == '__main__':
	print('All Available Sources: ')
	for s in get_sources():
		print('Source:', end='')
		print(s.to_obj())
	print()
	import sys
	sys.path.insert(0, '../filters')
	so = Source('test-source', description="This is just a test source.")
	built = so.from_obj({
		"type": "test-source",
		"alias": "test-source-alias",
		"data": {
			"auth": {
				"client_id": "ID_From_Registering_app",
				"client_secret": "Secret_from_registering_app",
				"password": "Your_password",
				"user_agent": "USE_A_RANDOM_ID_HERE",
				"username": "Your_Username"
			}
		},
		"filters": {
				"created_utc.min": '2017-11-08T05:18:19+00:00',
				"created_utc.max": 0,
				"score.min": 0,
				"author": "shadowmoose"
			}
	})
	print('Built Source Object: ', built)
	print('Loaded Filters:')
	for f in so.filters:
		print('\t', f)
	print('\n\nLoaded Data: ', end='')
	print(so.data)
