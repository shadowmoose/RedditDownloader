import os
import json
import sys

default_settings = {
    "auth": {
        "client_id": "ID_From_Registering_app",
        "client_secret": "Secret_from_registering_app",
        "password": "Your_password",
        "user_agent": "USE_A_RANDOM_ID_HERE",
        "username": "Your_Username"
    },
    "build_manifest": True,
    "last_started": 0,
    "output": {
        "base_dir": "./download/",
        "subdir_pattern": "/[subreddit]/",
        "file_name_pattern": "[title] - ([author])"
    }
}

class Settings(object):
	def __init__(self, file, can_save=True):
		self.vals = default_settings
		self.can_save = can_save
		self.settings_file = file
		if self.can_save and not os.path.isfile(self.settings_file):
			self.save()# Save defaults.
			print('Please configure the generated settings file before launching again.')
			print('Fill in your username/password, and register an app here: https://www.reddit.com/prefs/apps \nFill the app\'s information in as well.')
			sys.exit(1)
		if os.path.isfile(self.settings_file):
			with open(self.settings_file) as json_data:
				self.vals = json.load(json_data)
	#
	
	def set(self, key, value):
		self.vals[key] = value
		self.save()
	#
	
	def save(self):
		if not self.can_save:
			return
		with open(self.settings_file, 'w') as outfile:
			json.dump(self.vals, outfile, sort_keys=True, indent=4, separators=(',', ': '))
	#
	
	def get(self, key, default_val=None, save_if_default=False):
		if key in self.vals:
			return self.vals[key]
		elif save_if_default:
			self.set(key, default_val)
			return default_val
		return default_val
	#
	
	def get_save_location(self, sub):
		""" Used for internal fast access to the save path patterns. """
		out = self.get('output')
		if not out:
			print('!Malformed output settings. Using defaults.')
			return default_settings['output']
		return out[sub]
	#
	
	def save_base(self):
		""" The base folder pattern to save to. """
		return self.get_save_location('base_dir')
	
	def save_subdir(self):
		""" The save path's subdirectory pattern. """
		return self.get_save_location('subdir_pattern')
	
	def save_filename(self):
		""" The save path's filename pattern. """
		return self.get_save_location('file_name_pattern')