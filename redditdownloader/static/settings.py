import copy
import json
import os
import uuid


_file = None
_settings = dict()
_default_cat = 'misc'


def save():
	if _file is None:
		return False
	with open(_file, 'w') as o:
		o.write(to_json())
		print('-Saved Settings-')
	return True


def to_json():
	"""
	Converts the Settings into a JSON String, which this class is guaranteed to be capable of loading.
	"""
	out = to_obj(save_format=True, include_private=True)
	return json.dumps(out, indent=4, sort_keys=True, separators=(',', ': '))


def from_json(json_data):
	"""
	Apply all of the Settings data within the given JSON string.
	:param json_data:
	:return: True if the given data had to be adapted from an older version.
	"""
	loaded, converted = _adapt(json.loads(json_data))

	for cat, sets in loaded.items():
		for ky, val in sets.items():
			try:
				st = get(ky, cat=cat, full_obj=True)
				st.set(val)
			except KeyError as ke:
				print('Error loading setting:', ke)
	return converted


def load(filename):
	global _file
	_file = os.path.abspath(filename)
	try:
		with open(_file, 'r') as json_data:
			converted = from_json(json_data.read())
	except IOError:
		return False
	print('Loaded settings file [%s].' % filename)
	if converted:
		print('\tHad to convert from older settings, so saving updated version!')
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


def put(key, value, cat=None, save_after=True):
	s = get(key, cat=cat, full_obj=True)
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


def get_all():
	""" Get all Setting objects. Used for the help printout. """
	for __k, __v in _settings.items():
		for __key, _stt in __v.items():
			yield _stt


def get_sources():
	""" Builds and then returns a list of the Sources in this Settings config. """
	import sources
	return sources.load_sources(get('sources'))


def has_source_alias(alias):  # !cover - no sources yet
	""" Check if the given source alias exists. """
	sources = get_sources()
	for s in sources:
		if s.get_alias() == alias:
			return True
	return False


def add_source(new_source, prevent_duplicate=True, save_after=True):  # !cover - no sources yet
	""" Adds the given source to the JSON-encoded Settings data. Will not add a duplicate Source alias.
		Returns if the Source was added
	"""
	if prevent_duplicate and has_source_alias(new_source.get_alias()):
		return False
	new_sources = get_sources()
	new_sources.append(new_source)
	put('sources', [s.to_obj() for s in new_sources], save_after=save_after)
	return True


def remove_source(source, save_after=True):
	""" Removes the given Source from the list of sources, and resaves (if set). """
	new_sources = [s for s in get_sources() if s.get_alias() != source.get_alias()]
	put('sources', [s.to_obj() for s in new_sources], save_after=save_after)


class Setting(object):
	def __init__(self, name, value, desc='', etype='str', public=True, opts=None):
		self.name = name
		self._value = None
		self.type = str(etype)
		self.category = None
		self.public = public
		self.description = desc
		self.opts = self.set_opts(opts)
		self.set(value)

	def val(self):
		return copy.deepcopy(self._value)

	def set(self, val):
		if val is None and len(self.opts) > 0:
			val = self.opts[0][0]  # Default to first opt value, if opts are set.
		val = self.attempt_convert(val)
		if self.type not in val.__class__.__name__:
			raise TypeError('Invalid type for setting [%s]! %s != %s' % (self.name, self.type, val.__class__.__name__))
		if self.opts and val not in [x[0] for x in self.opts]:
			raise ValueError('Invalid value for setting [%s]! Value is not within given keys.' % val)
		self._value = val

	def set_cat(self, cat):
		self.category = cat.lower()

	def set_opts(self, opts):
		""" Parse the given opts array into this setting's Options, a named list of (value, description) pairs. """
		ret = None
		if opts:
			ret = []
			for o in opts:
				if not isinstance(o, tuple):
					o = (o, '')
				ret.append(o)
		return ret

	def to_obj(self):
		obj = {}
		for k, v in vars(self).items():
			if not k.startswith('_'):
				obj[k] = v
		obj['value'] = self.val()
		return obj

	def attempt_convert(self, val):
		if self.type == 'int':
			try:
				return int(float(val))
			except ValueError:
				pass
		if self.type == 'bool':
			accept = {True: ['1', 'true', 'yes'], False: ['0', 'none', 'false', 'no']}
			for k, v in accept.items():
				if any(str(val).lower() in x for x in v):
					return k
		return val

	def __str__(self):
		return str(self.to_obj())


# =========  DEFAULT SETTINGS  =========
add("auth", Setting("refresh_token", '', desc="Use this to safely authorize RMD to read your Reddit account."))
add("auth", Setting("rmd_client_key", 'v4XVrdEH_A-ZaA', desc="Change only if you know what you're doing.", public=False))
add("auth", Setting("user_agent", 'RMD-Scanner-%s' % uuid.uuid4(), desc="The user agent to identify as, wherever possible."))
add("auth", Setting("oauth_key", str(uuid.uuid4()), desc="Internal key.", public=False))

add("output", Setting("base_dir", os.getcwd() + '/download/', desc="The base directory to save to. Cannot contain tags."))
add("output", Setting("file_name_pattern", '[subreddit]/[title] - ([author])', desc="The ouput file name/path. Supports tags."))

add("processing", Setting("deduplicate_files", True, desc="Remove downloaded files if another copy already exists. Also compares images for visual similarity.", etype="bool"))

add("threading", Setting("concurrent_downloads", 5, desc="How many threads can download media at once.", etype="int"))
add("threading", Setting("console_clear_screen", True, desc="If it's okay to clear the terminal while running.", etype="bool"))
add("threading", Setting("display_refresh_rate", 5, desc="How often the UI should update progress, in seconds.", etype="int"))

add("interface", Setting("start_server", True, desc="If the WebUI should be available.", etype="bool"))
add("interface", Setting("browser", 'chrome-app', desc="Browser to auto-open UI in.", etype="str", opts=[('chrome-app', 'Chrome Application Mode (recommended)'), ('default browser', 'The default system browser'), ('off', "Don't auto-open a browser")]))
add("interface", Setting("keep_open", False, desc="If True, the WebUI will stay available after the browser closes.", etype='bool'))
add("interface", Setting("port", 7505, desc="The port to open the WebUI on.", etype="int"))
add("interface", Setting("host", 'localhost', desc="The host to bind on."))

add(None, Setting("meta-version", 5, etype="int", public=False))
add(None, Setting("sources", [{'alias': 'default-downloader', 'data': {}, 'filters': {}, 'type': 'personal-upvoted-saved'}], etype="list", public=False))
# ======================================


def _adapt(obj):  # !cover
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
		from sources import UpvotedSaved
		us = UpvotedSaved()  # This Source doesn't need any extra info, and it simulates original behavior.
		us.set_alias('default-downloader')
		obj['sources'].append(us.to_obj())
		version = 2
		print("Adapted from Settings version 1 -> 2!")
		converted = True

	if version == 2:
		# Version 2->3 saw addition of display config, for Threading.
		obj['meta-version'] = 3
		obj['threading'] = {
			"max_handler_threads": 5,
			"display_clear_screen": True,
			"display_refresh_rate": 5
		}
		version = 3
		print("Adapted from Settings version 2 -> 3!")
		converted = True

	if version == 3:
		# Version 3->4 saw the Manifest shift to SQLite, the Settings overhaul, and the WebUI.
		obj[_default_cat] = {}
		rm = []
		for k, v in obj.items():
			if isinstance(v, dict):
				continue
			if k not in ['build_manifest', 'last_started', 'deduplicate_files',
						 'client_id', 'client_secret', 'password', 'username']:
				obj[_default_cat][k] = v
			rm.append(k)
		obj[_default_cat]['meta-version'] = 4
		obj['output']['deduplicate_files'] = obj['deduplicate_files']
		for r in rm:
			del obj[r]
		obj['interface'] = {}
		# obj['interface']['start_server'] = False  # Default to old behavior.
		print("Adapted from Settings version 3 -> 4!")
		converted = True
		version = 4

	if version == 4:
		# Moved to SqlAlchemy and Multiprocessing.
		obj['processing'] = {'deduplicate_files': obj['output']['deduplicate_files']}
		obj['output']['file_name_pattern'] = \
			('%s/%s' % (obj['output']['subdir_pattern'], obj['output']['file_name_pattern'])).replace('//', '/')
		obj['threading']['console_clear_screen'] = obj['threading']['display_clear_screen']
		obj['threading']['concurrent_downloads'] = obj['threading']['max_handler_threads']
		del obj['output']['subdir_pattern']
		del obj['output']['deduplicate_files']
		del obj['threading']['display_clear_screen']
		del obj['threading']['max_handler_threads']
		print("Adapted from Settings version 4 -> 5!")
		obj[_default_cat]['meta-version'] = 5
		converted = True
		# version = 5

	return obj, converted


if __name__ == '__main__':
	for _k, _v in _settings.items():
		print(_k.title() + ':')
		for _key, stt in _v.items():
			print('\t%s: %s' % (_key, stt))
