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
	"deduplicate_files": True,
	"last_started": 0,
	"meta-version": 2,
	"output": {
		"base_dir": "./download/",
		"subdir_pattern": "/[subreddit]/",
		"file_name_pattern": "[title] - ([author])"
	},
	"sources":[
		{
			"alias": "default-downloader",
			"data": {},
			"filters": {},
			"type": "personal-upvoted-saved"
		}
	]
}

class Settings(object):
	def __init__(self, file, can_save=True, can_load=True):
		self.vals = default_settings
		self.can_save = can_save
		self.settings_file = file
		if can_load and not os.path.isfile(self.settings_file):
			self.save()# Save defaults.
			import console
			if console.confirm('Would you like to launch the first-time setup assistant?', True):
				import wizards.wizard as wizard
				print('\n\n')
				wizard.run(file)
			else:
				print('Please configure the generated settings file before launching again.')
				print('Fill in your username/password, and register an app here: https://www.reddit.com/prefs/apps \n'
					  'Fill the app\'s client information in as well.')
				sys.exit(1)
		if can_load and os.path.isfile(self.settings_file):
			with open(self.settings_file) as json_data:
				self.vals = self.adapt(json.load(json_data))

	
	def set(self, key, value):
		self.vals[key] = value
		self.save()

	
	def save(self):
		if not self.can_save:
			return
		with open(self.settings_file, 'w') as outfile:
			json.dump(self.vals, outfile, sort_keys=True, indent=4, separators=(',', ': '))

	
	def get(self, key, default_val=None):
		if key in self.vals:
			return self.vals[key]
		return default_val

	
	def get_save_location(self, sub):
		""" Used for internal fast access to the save path patterns. """
		out = self.get('output')
		if not out:
			print('!Malformed output settings. Using defaults.')
			return default_settings['output']
		return out[sub]


	def get_sources(self):
		""" Builds and then returns a list of the Sources in this Settings config. """
		from sources import source
		return source.get_sources( self.get('sources', []) )


	def has_source_alias(self, alias):
		""" Check if the given source alias exists. """
		sources = self.get_sources()
		for s in sources:
			if s.get_alias() == alias:
				return True
		return False


	def add_source(self, new_source):
		""" Adds the given source to the JSON-encoded Settings data. Will not add a duplicate Source alias.
			Returns if the Source was added
		"""
		if self.has_source_alias(new_source.get_alias()):
			return False
		new_sources = self.get_sources()
		new_sources.append(new_source)
		self._set_source_list(new_sources)
		return True


	def remove_source(self, source):
		""" Removes the given Source from the list of sources, and resaves. """
		new_sources = [s for s in self.get_sources() if s.get_alias() != source.get_alias()]
		self._set_source_list(new_sources)


	def _set_source_list(self, s_list):
		""" Internal, saves the given list of sources to JSON format. """
		self.set('sources', [s.to_obj() for s in s_list])


	def save_base(self):
		""" The base folder pattern to save to. """
		return self.get_save_location('base_dir')


	def save_subdir(self):
		""" The save path's subdirectory pattern. """
		return self.get_save_location('subdir_pattern')


	def save_filename(self):
		""" The save path's filename pattern. """
		return self.get_save_location('file_name_pattern')


	def adapt(self, obj):
		version = 1
		if 'meta-version' in obj:
			version = obj['meta-version']

		if version == 1:
			# Version 1->2 saw addition of Sources & Filters.
			obj['meta-version'] = 2
			obj['sources'] = {}
			from sources.my_upvoted_saved_source import UpvotedSaved
			us = UpvotedSaved()# This Source doesn't need any extra info, and it simulates original behavior.
			us.set_alias('default-downloader')
			obj['sources'].append(us.to_obj())
			print("Adapted from Settings version 1 -> 2!")
		return obj