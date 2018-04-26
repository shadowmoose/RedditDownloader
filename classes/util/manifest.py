import json
import time
import os.path
import gzip

from util import stringutil


class Manifest:
	def __init__(self, settings, load = True):
		""" Prepare the Manifest Builder. Optionally load information from the given file. """
		self.version = 2.0
		self.data = {'@meta':{'version': 0}}# Default to no version, which will be converted.
		self.file = stringutil.normalize_file(settings.save_base() + '/Manifest.json.gz')
		self._completed = []
		self._failed = []
		if load and os.path.isfile(self.file): #!cover
			try:
				with gzip.GzipFile(self.file, 'rb') as data_file:
					self.data = json.loads(data_file.read().decode('utf8'))
			except:
				stringutil.error('Failed to load Manifest at [%s]. Probably corrupt. Try removing the file.' % self.file)
				raise
		change, self.data = self._adapt(self.data)
		while change:
			change, self.data = self._adapt(self.data)
		#
		assert 'elements' in self.data
		assert 'completed' in self.data['elements']
		assert 'failed' in self.data['elements']
		self.og_count = len(self.data['elements']['completed']+ self.data['elements']['failed'])


	def build(self, loader):
		print('Manifest eles remaining: %s/%s' % (
			len(self.data['elements']['completed']+ self.data['elements']['failed']),
			self.og_count
		))

		# Add unprocessed manifest-loaded elements back to their respective lists, to not lose them if interrupted.
		self._completed+= self.data['elements']['completed']
		self._failed+= self.data['elements']['failed']

		
		with gzip.GzipFile(self.file, 'w') as outfile:
			obj = {
				'@meta':{
					'version': self.version,
					'timestamp': time.time(),
					'finished': loader.count_completed() == loader.count_total(),
					'number_completed': loader.count_completed(),
					'number_found' : loader.count_total(),
				},
				'elements':{'completed':self._completed, 'failed':self._failed},
			}
			outfile.write( json.dumps(obj, sort_keys=True, indent=4, separators=(',', ': ')).encode() )
			self.data = obj


	def push_ele(self, ele, cleanup = True):
		""" Checks if the given element is considered "done" or "failed", and pushes them to the relevant list.
			If "cleanup" is True, also removes this element from the loaded manifest list.
		"""
		if cleanup and self._contains_id(ele.id):
			self._delete_id(ele.id)
		files = ele.get_completed_files()
		if len(files)>0 and not any(False == files[key] for key in files):
			self._completed.append(ele.to_obj())
			return True
		else:
			self._failed.append(ele.to_obj())
			return False


	def url_completed(self, url):
		""" Checks if the manifest knows of an existing completed file for this URL.
			Returns ([true/false](exists or not), [file_path])
		"""
		for e in self._all_eles(): #!cover
			assert 'files' in e
			if url in e['files']:
				exists = (e['files'][url] is not None and e['files'][url] is not False)
				return exists, e['files'][url]
		return False, None


	def _all_eles(self):
		""" Wrapper method to get a combined list of all completed and failed eles loaded. """
		return self.data['elements']['completed']+ self.data['elements']['failed']


	def _contains_id(self, post_id): #!cover
		""" Checks if the given ID exists in the manifest. """
		for e in self._all_eles():
			if e['id'] == post_id:
				return True, e
		return False, None


	def _delete_id(self, ele_id):
		""" Remove the given ID from the completed or failed list. """
		for t in ['completed', 'failed']:
			for e in self.data['elements'][t]:
				if e['id'] == ele_id:
					self.data['elements'][t].remove(e)
					return True
		return False



	def _adapt(self, obj):
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