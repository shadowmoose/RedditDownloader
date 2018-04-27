import json
import time
import os.path
import gzip
import sqlite3
from contextlib import closing

from util import stringutil
from util import rwlock



""" Prepare the Manifest Builder. Optionally load information from the given file. """
version = None
_completed = []
_failed = []

conn = None
lock = rwlock.RWLock() # Custom Read/Write lock, with Writer priority.

''''# TODO: Change adapting to checking metadata table.
change, data = _adapt(data)
while change:
	change, data = _adapt(data)
#
assert 'elements' in data
assert 'completed' in data['elements']
assert 'failed' in data['elements']
og_count = len(data['elements']['completed']+ data['elements']['failed'])
'''


def create(file, base_dir = None):
	global conn
	with lock('w'):
		if base_dir is not None:
			file = stringutil.normalize_file(base_dir + '/' + file)
		build =  file == ':memory:' or not os.path.isfile(file)
		conn = sqlite3.connect(file)
		if build:
			with closing(conn.cursor()) as cur:
				cur.execute('''CREATE TABLE posts (
					id text PRIMARY KEY, author text, source_alias text, subreddit text, title text, type text
				)''')
				cur.execute('''CREATE TABLE urls (
					post_id text, url text, file_path text
				)''')
				cur.execute('''CREATE TABLE hashes (
					file_path text PRIMARY KEY, lastmtime int, hash text
				)''')
			conn.commit()
			print("Built DB.")
	print('Connected to DB.')


def push_ele(ele, cleanup = True):
	""" Checks if the given element is considered "done" or "failed", and pushes them to the relevant list.
		If "cleanup" is True, also removes this element from the loaded manifest list.
	"""
	#TODO


def url_completed(url):
	""" Checks if the manifest knows of an existing completed file for this URL.
		Returns ([true/false](exists or not), [file_path])
	"""
	#TODO


def _adapt(obj):
	""" Adjust the given data to fit the current manifest version.
		Should be called repeatedly on an object until it not longer returns true.
		Returns: ( [true/false](If changed), new_obj )
	"""
	v = obj['@meta']['version']
	if v == version:
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


def insert(eles):
	""" Inserts a given list of elements into the database. """
	with lock('w'), closing(conn.cursor()) as cur:
		for ele in eles:
			cur.execute('INSERT OR REPLACE INTO posts VALUES (?,?,?,?,?,?)',
				(ele['id'], ele['author'], ele['source_alias'], ele['subreddit'], ele['title'], ele['type'])
			)
			print(ele)
			cur.execute('DELETE FROM urls WHERE post_id = :id', {'id':ele['id']})
			for k,v in ele['files'].items():
				cur.execute('INSERT INTO urls VALUES (?,?,?)', (ele['id'], k, str(v) ))
		conn.commit()


def _select_fancy(table, cols, where = '', arg_dict=()):
	""" A boilerplate DB method for requesting specific fields, and getting a named dict back. """
	with lock('r'), closing(conn.cursor()) as cur:
		cur.execute('SELECT %s FROM %s WHERE %s' % (','.join(cols), table, where), arg_dict)
		ret = cur.fetchone()
		if not ret:
			return ret
		return dict(zip(cols, ret))


def hash_iterator():
	""" Opens an iterator that will cycle through all known file Hashes.
		Use gen.send(True) to kill early, otherwise be sure to iterate all the way through.
	"""
	_exit = None
	with lock('r'), closing(conn.cursor()) as cur:
		cur.execute('SELECT lastmtime, hash, file_path FROM hashes') #SELECT * FROM urls
		while _exit is None:
			ret = cur.fetchone()
			if ret is None:
				break
			_exit = (yield ret)
	#print('iterator closed.')
	if _exit is not None:
		yield None


def get_file_hash(f_path):
	""" Returns a dictionary of the given Hash info for the file, or None. """
	return _select_fancy('hashes', ['lastmtime', 'hash'], 'file_path = :fname', {'fname':f_path})


def put_file_hash(f_path, f_hash, f_lastmtime):
	""" Adds the given hash data for the given filename. """
	with lock('w'), closing(conn.cursor()) as cur:
		cur.execute('INSERT OR REPLACE INTO hashes (file_path, lastmtime, hash) VALUES (?,?,?)',
			(f_path, f_lastmtime, f_hash)
		)
		conn.commit()




if __name__ == '__main__':
	print('Testing Manifest - hardcoded paths mean this will probably only work for ShadowMoose.')

	#if os.path.isfile('./test.sqldb'):
	#	os.remove('./test.sqldb')

	create('test.sqldb', './')
	# noinspection PyProtectedMember
	#insert(_all_eles())

	print('Real Hash:', get_file_hash('fake_filename'))
	print('Fake Hash:', get_file_hash('fake-2'))

	print('\nIterating Hashes:')
	_hgen = hash_iterator()
	i = 1
	for h in _hgen:
		print('\tRet [%s]: ' % i, h)
		i+=1
		if i> 10:
			print('Test killing gen.')
			_hgen.send(True)
	print('Test done.')
