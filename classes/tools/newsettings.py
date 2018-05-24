import copy

_settings = dict()
_default_cat = 'Misc'


def add(cat, st):
	cat = cat.lower() if cat else _default_cat.lower()
	if cat not in _settings:
		_settings[cat] = dict()
	st.category = cat.lower()
	_settings[cat][st.name] = st


def get(key, default=None, full_obj=False, cat=None):
	cat = cat if cat else _default_cat.lower()
	if '.' in key:
		cat = key.split('.')[0].lower()
		key = key.split('.', 2)[1]
	if cat in _settings and key in _settings[cat]:
		rs = _settings[cat][key]
		return rs.val() if not full_obj else rs
	return default


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
			raise TypeError(f'Invalid type for new setting value! {self.type} != {type(val.__class__.__name__)}')
		self.value = val

	def set_cat(self, cat):
		self.category = cat.lower()

	def __str__(self):
		obj = {}
		for k, v in vars(self).items():
			if not k.startswith('_'):
				obj[k] = v
		return str(obj)


# =========  DEFAULT SETTINGS  =========
add("auth", Setting("client_id", 'ID_From_Registering_app', desc="TODO"))
add("auth", Setting("client_secret", 'Secret_from_registering_app', desc="TODO"))
add("auth", Setting("password", 'Your_password', desc="TODO"))
add("auth", Setting("user_agent", 'USE_A_RANDOM_ID_HERE', desc="TODO"))
add("auth", Setting("username", 'Your_Username', desc="TODO"))

add(None, Setting("meta-version", 4, etype="int", public=False))
add(None, Setting("sources", [{'alias': 'default-downloader', 'data': {}, 'filters': {}, 'type': 'personal-upvoted-saved'}], etype="list", public=False))

add("output", Setting("base_dir", './download/', desc="The base directory to save to. Cannot contain tags."))
add("output", Setting("subdir_pattern", '/[subreddit]/', desc="The directory path, within the base_dir, to save files to."))
add("output", Setting("file_name_pattern", '[title] - ([author])', desc="The ouput file name."))
add("output", Setting("deduplicate_files", True, desc="Check all files to assure they're unique. Also deduplicates similar-looking images.", etype="bool"))

add("threading", Setting("max_handler_threads", 5, desc="How many threads can download posts at once.", etype="int"))
add("threading", Setting("display_clear_screen", True, desc="If it's okay to clear the terminal while running.", etype="bool"))
add("threading", Setting("display_refresh_rate", 5, desc="How often the UI should update progress.", etype="int"))

add("ui", Setting("start_server", True, desc="If the WebUI should automatically start.", etype="bool"))
add("ui", Setting("open_browser", True, desc="If the WebUI should open the browser on startup.", etype="bool"))
add("ui", Setting("port", 8000, desc="The port to open the WebUI on.", etype="int"))
add("ui", Setting("socket", 'localhost', desc="The interface to bind on."))
# ======================================


if __name__ == '__main__':
	print('\n\nTest val:', get('output.base_dir'))
	print('Test full:', get('output.base_dir', full_obj=True))

	for _k, _v in _settings.items():
		print(f'{_k.title()}:')
		for _key, stt in _v.items():
			print(f'\t{_key}: {stt}')
