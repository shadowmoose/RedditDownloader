import json
import time
import os.path
import gzip
import sqlite3
from contextlib import closing

from util import stringutil
from util import rwlock


class Manifest:
	def __init__(self, save_base):
		""" Prepare the Manifest Builder. Optionally load information from the given file. """
		self.version = 2.0
		self.data = {'@meta':{'version': 0}}# Default to no version, which will be converted.
		self.file = stringutil.normalize_file(save_base + '/Manifest.json.gz')
		self._completed = []
		self._failed = []

		self.conn = None
		self.lock = rwlock.RWLock() # Custom Read/Write lock, with Writer priority.

		# TODO: Change adapting to checking metadata table.
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


	def create(self, file):
		with self.lock('w'):
			build =  file == ':memory:' or not os.path.isfile(file)
			self.conn = sqlite3.connect(file)
			if build:
				with closing(self.conn.cursor()) as cur:
					cur.execute('''CREATE TABLE posts (
						id text PRIMARY KEY, author text, source_alias text, subreddit text, title text, type text
					)''')
					cur.execute('''CREATE TABLE urls (
						post_id text, url text, file_path text
					)''')
					cur.execute('''CREATE TABLE hashes (
						file_path text PRIMARY KEY, lastmtime int, hash text
					)''')
				self.conn.commit()
				print("Built DB.")
		print('Connected to DB.')


	def insert(self, eles):
		""" Inserts a given list of elements into the database. """
		with self.lock('w'), closing(self.conn.cursor()) as cur:
			for ele in eles:
				cur.execute('INSERT OR REPLACE INTO posts VALUES (?,?,?,?,?,?)',
					(ele['id'], ele['author'], ele['source_alias'], ele['subreddit'], ele['title'], ele['type'])
				)
				print(ele)
				cur.execute('DELETE FROM urls WHERE post_id = :id', {'id':ele['id']})
				for k,v in ele['files'].items():
					cur.execute('INSERT INTO urls VALUES (?,?,?)', (ele['id'], k, str(v) ))
			self.conn.commit()


	def _select_fancy(self, table, cols, where = '', arg_dict=()):
		""" A boilerplate DB method for requesting specific fields, and getting a named dict back. """
		with self.lock('r'), closing(self.conn.cursor()) as cur:
			cur.execute('SELECT %s FROM %s WHERE %s' % (','.join(cols), table, where), arg_dict)
			ret = cur.fetchone()
			if not ret:
				return ret
			return dict(zip(cols, ret))


	def hash_iterator(self):
		""" Opens an iterator that will cycle through all known file Hashes.
			Use gen.send(True) to kill early, otherwise be sure to iterate all the way through.
		"""
		with self.lock('r'), closing(self.conn.cursor()) as cur:
			cur.execute('SELECT lastmtime, hash, file_path FROM hashes')
			_exit = None
			while _exit is None:
				ret = cur.fetchone()
				if ret is None:
					break
				_exit = (yield ret)
		print('iterator closed.')
		yield None


	def get_file_hash(self, f_path):
		""" Returns a dictionary of the given Hash info for the file, or None. """
		return self._select_fancy('hashes', ['lastmtime', 'hash'], 'file_path = :fname', {'fname':f_path})


	def put_file_hash(self, f_path, f_hash, f_lastmtime):
		""" Adds the given hash data for the given filename. """
		with self.lock('w'), closing(self.conn.cursor()) as cur:
			cur.execute('INSERT OR REPLACE INTO hashes (file_path, lastmtime, hash) VALUES (?,?,?)',
				(f_path, f_lastmtime, f_hash)
			)
			self.conn.commit()



if __name__ == '__main__':
	print('Testing Manifest - hardcoded paths mean this will probably only work for ShadowMoose.')
	_man = Manifest('../../../download/')
	if os.path.isfile('./test.sqldb'):
		os.remove('./test.sqldb')

	_man.create('test.sqldb')
	# noinspection PyProtectedMember
	_man.insert(_man._all_eles())

	print('Real Hash:', _man.get_file_hash('fake_filename'))
	print('Fake Hash:', _man.get_file_hash('fake-2'))

	_hgen = _man.hash_iterator()
	i = 1
	for h in _hgen:
		print('Ret [%s]: ' % i, h)
		i+=1
		if i> 10:
			print('Kill gen.')
			_hgen.send(True)
	print('Test done.')
