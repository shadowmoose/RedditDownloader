"""
	Generic Source class, all actual sources should override this.
"""
from filters import filter


class Source:
	""" Source objects have simply:
		type - The ID of which Source object to load as
		data - The object that contains anything each specific source type may need to save/load.

		Source Classes should override init() (to set type), get_elements() & setup_wizard()
	"""
	def __init__(self, source_type):
		self.type = source_type
		self.filters = []
		self.data = {}


	def get_elements(self):
		"""  Tells this Source to build and return a list of RedditElements. """
		pass


	def setup_wizard(self):
		"""  Make this Souce object prompt the user for the information it needs to retrieve data. """
		pass


	def from_obj(self, obj):
		"""  Build this Source from the data model loaded.
			Returns False if this Source doesn't match the given object. If True, this Source has been initialized.
		"""
		if self.type != obj['type']:
			return False
		self.data = obj['data']
		self._load_filters(obj)
		return True


	def to_obj(self):
		"""  Convert this Source into a data model that can be output to the Settings file.  """
		out = {'type':self.type, 'filters':[], 'data':self.data}
		for f in self.filters:
			out['filters'].append(f.to_obj())
		return out


	def _load_filters(self, data):
		""" Builds the list of filters this object needs. """
		if 'filters' not in data:
			return False
		self.filters = filter.get_filters(data['filters'])




"""
"sources":[
	{
		"type": "test-source",
		"data":{
			"auth": {
				"client_id": "ID_From_Registering_app",
				"client_secret": "Secret_from_registering_app",
				"password": "Your_password",
				"user_agent": "USE_A_RANDOM_ID_HERE",
				"username": "Your_Username"
			}
		},
		"filters":{
				"created_utc.min": 0,
				"created_utc.max": 0,
				"score.min": 0,
				"author": "shadowmoose"
			}
	}
]

"""

if __name__ == '__main__':
	import sys
	sys.path.insert(0, '../filters')
	so = Source('test-source')
	built = so.from_obj({
		"type": "test-source",
		"data":{
			"auth": {
				"client_id": "ID_From_Registering_app",
				"client_secret": "Secret_from_registering_app",
				"password": "Your_password",
				"user_agent": "USE_A_RANDOM_ID_HERE",
				"username": "Your_Username"
			}
		},
		"filters":{
				"created_utc.min": 0,
				"created_utc.max": 0,
				"score.min": 0,
				"author": "shadowmoose"
			}
	})
	print('Built Source Object: ', built)
	print('Loaded Filters:')
	for f in so.filters:
		print('\t',f)
	print('\n\nLoaded Data: ', end='')
	print(so.data)