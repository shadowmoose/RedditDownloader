import json
import time
from colorama import Fore
import os.path
import gzip

import stringutil


class Manifest:
	def __init__(self, settings, load = True):
		""" Prepare the Manifest Builder. Optionally load information from the given file. """
		self.version = 2.0
		self.data = {'@meta':{'version': 0}}# Default to no version, which will be converted.
		self.file = stringutil.normalize_file(settings.save_base()+'/Manifest.json.gz')
		if load and os.path.isfile(self.file):
			try:
				with gzip.GzipFile(self.file, 'rb') as data_file:
					self.data = json.loads(data_file.read().decode('utf8'))
			except:
				stringutil.error('Failed to load Manifest at [%s]. Probably corrupt. Try removing the file.' % self.file)
				raise
		change, self.data = self.adapt(self.data)
		while change:
			change, self.data = self.adapt(self.data)
		#


	def build(self, loader):
		gen = loader.get_elements()
		
		done = []
		failed = []
		for ele in gen:
			files = ele.get_completed_files()
			if len(files)>0 and not any(False == files[key] for key in files):
				done.append(ele.to_obj())
			else:
				failed.append(ele.to_obj())
		#
		
		with gzip.GzipFile(self.file, 'w') as outfile:
			obj = {
				'@meta':{
					'version': self.version,
					'timestamp': time.time(),
					'finished': loader.count_completed() == loader.count_total(),
					'number_completed': loader.count_completed(),
					'number_found' : loader.count_total(),
				},
				'elements':{'completed':done, 'failed':failed},
			}
			outfile.write( json.dumps(obj, sort_keys=True, indent=4, separators=(',', ': ')).encode() )
			self.data = obj


	def url_completed(self, url):
		""" Checks if the manifest knows of an existing completed file for this URL.
			Returns ([true/false](exists or not), [file_path])
		"""
		assert 'elements' in self.data
		assert 'completed' in self.data['elements']
		for e in self.data['elements']['completed']:
			assert 'files' in e
			if url in e['files']:
				return True, e['files'][url]
		return False, None


	def adapt(self, obj):
		""" Adjust the given data to fit the current manifest version.
			Should be called repeatedly on an object until it not longer returns true.
			Returns: ( [true/false](If changed), new_obj )
		"""
		v = obj['@meta']['version']
		if v == self.version:
			return False, obj

		if v <= 1:
			# We don't adapt from version <= 1, because of missing data.
			# Still adjusts to 2.0 format, to future-proof the baseline format.
			return True, {
				'@meta':{
					'version': 2.0,
					'timestamp': time.time(),
					'finished': False,
					'number_completed': 0,
					'number_found' : 0,
				},
				'elements':{'completed':[], 'failed':[]},
			}