import copy
import json
import os


_file = ''
_settings = dict()
_default_cat = 'misc'



def save():
	out = to_obj(save_format=True, include_private=True)
	with open(_file, 'w') as o:
		o.write(json.dumps(out, indent=4, sort_keys=True, separators=(',', ': ')))
	print('Saved Settings.')


def load(filename):
	global _file
	_file = os.path.abspath(filename)
	try:
		with open(_file, 'r') as json_data:
			loaded, converted = _adapt(json.load(json_data))
	except IOError:
		return False
	for cat, sets in loaded.items():
		for ky, val in sets.items():
			st = get(ky, cat=cat, full_obj=True)
			st.set(val)
	print('Loaded settings file [%s].' % filename)
	if converted:
		print('Had to convert from older settings, so saving updated version!')
		save()
	return True


def add(cat, st):
	cat = cat.lower() if cat else _default_cat.lower()
	if cat not in _settings:
		_settings[cat] = dict()
	st.category = cat.lower()
	_settings[cat][st.name] = st


def get(key, full_obj=False, cat=None):
	cat = cat if cat else _default_cat.lower()
	if '.' in key:
		cat = key.split('.')[0].lower()
		key = key.split('.', 2)[1]
	if cat in _settings and key in _settings[cat]:
		rs = _settings[cat][key]
		return rs.val() if not full_obj else rs
	raise KeyError('The given setting (%s) does not exist!' % key)


def put(key, value, save_after=True):
	s = get(key, full_obj=True)
	s.set(value)
	if save_after:
		save()


def to_obj(save_format=False, include_private=True):
	obj = dict()
	for cat, sets in _settings.items():
		if cat not in obj:
			obj[cat] = [] if not save_format else {}
		for key, opt in sets.items():
			if not include_private and not opt.public:
				continue
			if save_format:
				obj[cat][key] = opt.val()
			else:
				obj[cat].append(opt.to_obj())
	return obj



def get_sources():
	""" Builds and then returns a list of the Sources in this Settings config. """
	from classes.sources import source
	return source.get_sources( get('sources') )

def has_source_alias(alias): #!cover - no sources yet
	""" Check if the given source alias exists. """
	sources = get_sources()
	for s in sources:
		if s.get_alias() == alias:
			return True
	return False

def add_source(new_source): #!cover - no sources yet
	""" Adds the given source to the JSON-encoded Settings data. Will not add a duplicate Source alias.
		Returns if the Source was added
	"""
	if has_source_alias(new_source.get_alias()):
		return False
	new_sources = get_sources()
	new_sources.append(new_source)
	put('sources', [s.to_obj() for s in new_sources])
	return True

def remove_source(source): #!cover - no sources yet
	""" Removes the given Source from the list of sources, and resaves. """
	new_sources = [s for s in get_sources() if s.get_alias() != source.get_alias()]
	put('sources', [s.to_obj() for s in new_sources])


def save_base():
	""" The base folder pattern to save to. """
	return get('output.base_dir')

def save_subdir():
	""" The save path's subdirectory pattern. """
	return get('output.subdir_pattern')

def save_filename():
	""" The save path's filename pattern. """
	return get('output.file_name_pattern')


class Setting(object):
	def __init__(self, name, value, desc='', etype='str', public=True):
		self.name = name
		self.value = None
		self.type = str( etype )
		self.category = None
		self.public = public
		self.description = desc
		self.set(value)

	def val(self):
		return copy.deepcopy(self.value)

	def set(self, val):
		if val.__class__.__name__ != self.type:
			raise TypeError('Invalid type for new setting value! %s != %s' % (self.type, type(val.__class__.__name__)))
		self.value = val

	def set_cat(self, cat):
		self.category = cat.lower()

	def to_obj(self):
		obj = {}
		for k, v in vars(self).items():
			if not k.startswith('_'):
				obj[k] = v
		return obj

	def __str__(self):
		return str(self.to_obj())


# =========  DEFAULT SETTINGS  =========
add("auth", Setting("client_id", 'ID_From_Registering_app', desc="TODO"))
add("auth", Setting("client_secret", 'Secret_from_registering_app', desc="TODO"))
add("auth", Setting("password", 'Your_password', desc="TODO"))
add("auth", Setting("user_agent", 'USE_A_RANDOM_ID_HERE', desc="TODO"))
add("auth", Setting("username", 'Your_Username', desc="TODO"))

add("output", Setting("base_dir", './download/', desc="The base directory to save to. Cannot contain tags."))
add("output", Setting("subdir_pattern", '/[subreddit]/', desc="The directory path, within the base_dir, to save files to."))
add("output", Setting("file_name_pattern", '[title] - ([author])', desc="The ouput file name."))
add("output", Setting("deduplicate_files", True, desc="Check all files to assure they're unique. Also deduplicates similar-looking images.", etype="bool"))

add("threading", Setting("max_handler_threads", 5, desc="How many threads can download posts at once.", etype="int"))
add("threading", Setting("display_clear_screen", True, desc="If it's okay to clear the terminal while running.", etype="bool"))
add("threading", Setting("display_refresh_rate", 5, desc="How often the UI should update progress.", etype="int"))

add("interface", Setting("start_server", True, desc="If the WebUI should automatically start.", etype="bool"))
add("interface", Setting("browser", 'chrome-app', desc="Browser mode to open UI in. Set to 'off' to disable auto-open, or 'default' for default system browser.", etype="str"))
add("interface", Setting("keep_open", False, desc="If True, the WebUI will keep running as a webserver.", etype='bool'))
add("interface", Setting("port", 8000, desc="The port to open the WebUI on.", etype="int"))
add("interface", Setting("host", 'localhost', desc="The host to bind on."))

add(None, Setting("meta-version", 4, etype="int", public=False))
add(None, Setting("sources", [{'alias': 'default-downloader', 'data': {}, 'filters': {}, 'type': 'personal-upvoted-saved'}], etype="list", public=False))
# ======================================



def _adapt(obj): #!cover
	""" Convert old versions of the Settings files up to the newest version. """
	version = 1
	converted = False
	if 'meta-version' in obj:
		version = obj['meta-version']
	elif _default_cat in obj and 'meta-version' in obj[_default_cat]:
		version = obj[_default_cat]['meta-version']

	if version == 1:
		# Version 1->2 saw addition of Sources & Filters.
		obj['meta-version'] = 2
		obj['sources'] = {}
		from classes.sources.my_upvoted_saved_source import UpvotedSaved
		us = UpvotedSaved()# This Source doesn't need any extra info, and it simulates original behavior.
		us.set_alias('default-downloader')
		obj['sources'].append(us.to_obj())
		version = 2
		print("Adapted from Settings version 1 -> 2!")
		converted = True

	if version == 2:
		# Version 2->3 sees addition of display config, for Threading.
		obj['meta-version'] = 3
		obj['threading'] = {
			"max_handler_threads":5,
			"display_clear_screen":True,
			"display_refresh_rate":5
		}
		version = 3
		print("Adapted from Settings version 2 -> 3!")
		converted = True

	if version == 3:
		obj[_default_cat] = {}
		rm = []
		for k, v in obj.items():
			if isinstance(v, dict):
				continue
			if not k in ['build_manifest', 'last_started', 'deduplicate_files']:
				obj[_default_cat][k] = v
			rm.append(k)
		obj[_default_cat]['meta-version'] = 4
		obj['output']['deduplicate_files'] = obj['deduplicate_files']
		for r in rm:
			del obj[r]
		print("Adapted from Settings version 3 -> 4!")
		converted = True

	return obj, converted


if __name__ == '__main__':
	for _k, _v in _settings.items():
		print(_k.title()+ ':')
		for _key, stt in _v.items():
			print('\t%s: %s' % (_key, stt))
