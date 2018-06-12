import os.path
import sqlite3
from contextlib import closing

from classes.util import stringutil
from classes.util import rwlock


version = '2.0'

conn = None
lock = rwlock.RWLock() # Custom Read/Write lock, with Writer priority.


def create(file):
	global conn, version
	with lock('w'):
		file = stringutil.normalize_file(file)
		build =  file == ':memory:' or not os.path.isfile(file)
		conn = sqlite3.connect(file, check_same_thread=False)
		if build:
			with closing(conn.cursor()) as cur:
				cur.execute('''CREATE TABLE posts (
					id text PRIMARY KEY,
					author text COLLATE NOCASE,
					source_alias text COLLATE NOCASE,
					subreddit text COLLATE NOCASE,
					title text COLLATE NOCASE,
					type text COLLATE NOCASE,
					parent text COLLATE NOCASE,
					body text COLLATE NOCASE
				)''')
				cur.execute('''CREATE TABLE urls (
					post_id text, url text, file_path text COLLATE nocase
				)''')
				cur.execute('''CREATE TABLE hashes (
					file_path text PRIMARY KEY COLLATE nocase, lastmtime int, hash text
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


def check_legacy(base_dir):
	""" Moves elements from legacy manifest, if one exists, to the new DB. """
	if os.path.exists('./Manifest.json.gz'):
		stringutil.print_color(stringutil.Fore.GREEN,'\n\nCONVERTING LEGACY MANIFEST...')
		from classes.tools import manifest_converter as mc
		data = mc.load('./Manifest.json.gz')
		mc.convert(base_dir, data)
		os.rename('./Manifest.json.gz', './Legacy - Manifest.json.gz')
		print('Finished conversion.\n\n')


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


def direct_insert_post(_id, author, source_alias, subreddit, title, _type, files, parent, body):
	""" For legacy conversions, expose direct access to element insertion. """
	with lock('w'), closing(conn.cursor()) as cur:
		cur.execute('INSERT OR REPLACE INTO posts (id, author, source_alias, subreddit, title, type, parent, body) '
					'VALUES (?,?,?,?,?,?,?,?)',
					(_id, author, source_alias, subreddit, title, _type, parent, body)
		)
		#print(ele)
		cur.execute('DELETE FROM urls WHERE post_id = :id', {'id':_id})
		for k,v in files.items():
			cur.execute('INSERT INTO urls VALUES (?,?,?)', (_id, k, str(v) ))
		conn.commit()


def insert_post(reddit_ele):
	""" Inserts a given list of elements into the database. """
	ele = reddit_ele.to_obj()
	direct_insert_post(ele['id'], ele['author'], ele['source_alias'], ele['subreddit'], ele['title'], ele['type'], ele['files'], ele['parent'], ele['body'])


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


def get_searchable_fields():
	""" Gets the set of explicitly whitelisted searchable Post fields. """
	return {'author', 'body', 'title', 'subreddit', 'source_alias'}


def search_posts(fields=(), term=''):
	""" Search for Posts, checking the given fields (must be whitelisted strings) for a matching (LIKE) term. """
	if len(fields) == 0 or not set(fields).issubset(get_searchable_fields()):
		stringutil.error('Invalid search field(s): %s' % fields)
		return None
	with lock('r'), closing(conn.cursor()) as cur:
		all_fields = "||' '||".join(fields)
		cur.execute('SELECT * FROM posts WHERE (%s) LIKE :term ORDER BY parent DESC, title' % all_fields, {'term':'%%%s%%' % term})
		names = [description[0] for description in cur.description]
		for p in cur:
			yield dict(zip(names, p))
'''
SELECT p.*, COUNT(*) AS 'file_count' FROM posts p
LEFT JOIN urls u
	ON u.post_id = p.id
where
	(p.title||' '||p.author||' '||p.subreddit||' '||p.body||' '||p.source_alias) LIKE '%term%'
	AND u.file_path not in ('None', 'False')
GROUP BY
	p.id
ORDER BY
	p.parent DESC, p.title

'''


def _expose_testing_cursor():
	"""
		This function exists ONLY FOR TESTING USES, where rolling functions may not make sense.
		It is decidedly not thread-safe, and will wreck everything if any Threads are still running.
	"""
	return conn.cursor()

