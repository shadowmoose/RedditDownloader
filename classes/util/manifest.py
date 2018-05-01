import time
import os.path
import sqlite3
from contextlib import closing

from classes.util import stringutil
from classes.util import rwlock


version = '1.0'

conn = None
lock = rwlock.RWLock() # Custom Read/Write lock, with Writer priority.

#TODO: Change adapting to checking metadata table.
''''
change, data = _adapt(data)
while change:
	change, data = _adapt(data)
#
assert 'elements' in data
assert 'completed' in data['elements']
assert 'failed' in data['elements']
og_count = len(data['elements']['completed']+ data['elements']['failed'])
'''


def create(file):
	global conn, version
	with lock('w'):
		file = stringutil.normalize_file(file)
		build =  file == ':memory:' or not os.path.isfile(file)
		conn = sqlite3.connect(file, check_same_thread=False)
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
				cur.execute('''CREATE TABLE metadata (
					meta_key text PRIMARY KEY, meta_val text
				)''')
				conn.commit()
			with closing(conn.cursor()) as cur:
				cur.execute('INSERT INTO metadata VALUES (?,?)', ('version', version))
				cur.execute('INSERT INTO metadata VALUES (?,?)', ('author', 'ShadowMoose'))
				cur.execute('INSERT INTO metadata VALUES (?,?)', ('website', 'https://goo.gl/hgBxN4'))
				conn.commit()
			print("Built DB.")
	print('Connected to DB.')


def _adapt(obj): #!cover
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


def get_metadata(key, default=None): #!cover
	"""  Simple function for looking up DB metadata.  """
	with lock('r'), closing(conn.cursor()) as cur:
		cur.execute('SELECT meta_val FROM metadata WHERE meta_key=:k', {'k':key})
		ret = cur.fetchone()
		if ret is None:
			ret = default
		return ret[0]


def set_metadata(key, value): #!cover
	"""  Simple function for setting DB metadata.  """
	with lock('w'), closing(conn.cursor()) as cur:
		cur.execute('INSERT OR REPLACE INTO metadata VALUES (?,?)', (key, str(value) ))
		conn.commit()


def insert_post(reddit_ele):
	""" Inserts a given list of elements into the database. """
	ele = reddit_ele.to_obj()
	with lock('w'), closing(conn.cursor()) as cur:
		cur.execute('INSERT OR REPLACE INTO posts VALUES (?,?,?,?,?,?)',
			(ele['id'], ele['author'], ele['source_alias'], ele['subreddit'], ele['title'], ele['type'])
		)
		#print(ele)
		cur.execute('DELETE FROM urls WHERE post_id = :id', {'id':ele['id']})
		for k,v in ele['files'].items():
			cur.execute('INSERT INTO urls VALUES (?,?,?)', (ele['id'], k, str(v) ))
		conn.commit()


def get_url_info(url):
	""" Returns any information about the given URL, if the Manifest has downloaded it before. """
	dat = _select_fancy('urls', ['url', 'post_id', 'file_path'], 'url = :ur', {'ur':url})
	if dat: #!cover
		if dat['file_path'] == 'False':
			dat['file_path'] = False
		if dat['file_path'] == 'None':
			dat['file_path'] = None
	return dat


def remap_filepath(old_path, new_filepath):
	""" Called if a better version of a file is found, this updates them all to the new location. """
	old_path = stringutil.normalize_file(old_path)
	new_filepath = stringutil.normalize_file(new_filepath)
	with lock('w'), closing(conn.cursor()) as cur: #!cover
		cur.execute('UPDATE urls SET file_path=:nfp WHERE file_path = :ofp', {'nfp':new_filepath, 'ofp':old_path})
		conn.commit()


def _select_fancy(table, cols, where = '', arg_dict=()):
	""" A boilerplate DB method for requesting specific fields, and getting a named dict back. Not injection-proof. """
	with lock('r'), closing(conn.cursor()) as cur: #!cover
		cur.execute('SELECT %s FROM %s WHERE %s' % (','.join(cols), table, where), arg_dict)
		ret = cur.fetchone()
		if not ret:
			return ret
		return dict(zip(cols, ret))


def hash_iterator(hash_len):
	""" Opens an iterator that will cycle through all known file Hashes.
		Use gen.send(True) to kill early, otherwise be sure to iterate all the way through.
	"""
	_exit = None
	with lock('r'), closing(conn.cursor()) as cur:
		#Test: SELECT * FROM urls
		cur.execute('SELECT lastmtime, hash, file_path FROM hashes WHERE length(hash) = :hash', {'hash':hash_len})
		while _exit is None:
			ret = cur.fetchone()
			if ret is None:
				break
			if ret:
				ret = dict(zip(['lastmtime', 'hash', 'file_path'], ret))
			_exit = (yield ret)
	#print('iterator closed.')
	if _exit is not None:
		yield None #!cover


def get_file_hash(f_path):
	""" Returns a dictionary of the given Hash info for the file, or None. """
	f_path = stringutil.normalize_file(f_path)
	return _select_fancy('hashes', ['lastmtime', 'hash'], 'file_path = :fname', {'fname':f_path})


def put_file_hash(f_path, f_hash, f_lastmtime):
	""" Adds the given hash data for the given filename. """
	f_path = stringutil.normalize_file(f_path)
	with lock('w'), closing(conn.cursor()) as cur:
		cur.execute('INSERT OR REPLACE INTO hashes (file_path, lastmtime, hash) VALUES (?,?,?)',
			(f_path, f_lastmtime, f_hash)
		)
		conn.commit()


def remove_file_hash(f_path):
	""" Remove any hashes for the given path. """
	f_path = stringutil.normalize_file(f_path)
	with lock('w'), closing(conn.cursor()) as cur:
		cur.execute('DELETE FROM hashes WHERE file_path=:fp',{'fp':f_path})
		conn.commit()


def _expose_testing_cursor():
	"""
		This function exists ONLY FOR TESTING USES, where rolling functions may not make sense.
		It is decidedly not thread-safe, and will wreck everything if any Threads are still running.
	"""
	return conn.cursor()


if __name__ == '__main__':
	os.chdir(input('Enter a base dir: '))
	print('Testing Manifest...')

	create('manifest.sqldb')
	# noinspection PyProtectedMember
	#insert(_all_eles())

	print('Real Hash:', get_file_hash('fake_filename'))
	print('Fake Hash:', get_file_hash('fake-2'))

	print('\nIterating Hashes:')
	_hgen = hash_iterator(10)
	i = 1
	for h in _hgen:
		print('\tRet [%s]: ' % i, h)
		i+=1
		if i> 10:
			print('Test killing gen.')
			_hgen.send(True)

	print('\nTesting Files:')
	_c = _expose_testing_cursor()
	_c.execute('SELECT post_id, file_path FROM urls')
	_failed = 0
	_invalid = 0
	_total = 0
	for r in _c.fetchall():
		_pid = r[0]
		_file = r[1]
		_total+=1
		if _file == 'None' or _file == 'False':
			_failed+=1
			continue
		if not os.path.exists(_file):
			print(_pid, _file)
			_invalid+=1
	print('%s total files.' % _total)
	print('%s invalid file paths.' % _invalid)
	print('%s failed files.' % _failed)
	print('Test done.')
