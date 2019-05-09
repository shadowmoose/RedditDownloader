import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))


import gzip
import json
import argparse
from static import settings
from static import praw_wrapper as rd
from static import stringutil
from processing.wrappers.redditelement import RedditElement
import sql
import uuid
from processing import name_generator
from processing.wrappers import rel_file
import shutil
from static import console
import sqlite3


parser = argparse.ArgumentParser(
	description="Tool for converting old RMD manifests.")
parser.add_argument("--settings", help="Path to custom Settings file.", type=str, metavar='', default=None)
parser.add_argument("--og_base_dir_path", help="The directory RMD was originally saving in.", type=str, metavar='', default=None)
parser.add_argument("--og_base_dir_name", help="The exact 'base_dir' path used in the original settings.", type=str, metavar='', default=None)
parser.add_argument("--manifest_gz", help="The legacy Manifest.gz file, if exists.", type=str, metavar='', default=None)
parser.add_argument("--manifest_sql", help="The legacy SQLite db from 2.0+, if exists.", type=str, metavar='', default=None)
parser.add_argument("--new_save_dir", help="The path to the new save directory.", type=str, metavar='', default=None)
args, unknown_args = parser.parse_known_args()


class PendingPost:
	def __init__(self, reddit_id, files, source, title, reddit_ele=None):
		self.reddit_id = reddit_id
		self.title = title
		self.files = files
		self.source = source
		self.ele = RedditElement(reddit_ele) if reddit_ele else None

	def __str__(self):
		return "<Post ID: %s, Files: %s, Ele: %s>" % (self.reddit_id, self.files, True if self.ele else False)


class FailedPost(dict):
	def __init__(self, reddit_id, title, known_files, reason):
		self.reddit_id = reddit_id
		self.title = title
		self.files = {}
		self.failure_reason = reason
		for url, file in known_files.items():
			if file:
				self.files[url] = file
		dict.__init__(self, **self.__dict__)


class GZManifest:
	def __init__(self, gz_file, og_base):
		self.file = gz_file
		self.og_base = stringutil.normalize_file(og_base).replace('\\', '/')
		self.failed = []

	def load_completed(self):
		with gzip.GzipFile(self.file, 'rb') as data_file:
			eles = json.loads(data_file.read().decode('utf8'))
			return eles['elements']['completed'] + eles['elements']['failed']

	def find_comment(self, e):
		""" Legacy RedditElement Comments incorrectly grabbed the ID of their parent as their own. """
		if len(e['urls']) == 0:
			return None
		for c in rd.get_submission_comments(e['id']):
			try:
				c_urls = stringutil.html_elements(c.body_html, 'a', 'href')
			except AttributeError:
				continue
			if len(c_urls) == 0:
				continue
			if all(u in c_urls for u in e['urls']):
				return c

	def convert(self):
		for e in self.load_completed():
			com = None
			for k, v in e['files'].items():
				if v:
					fn = stringutil.normalize_file(v).replace('\\', '/')
					if self.og_base not in fn:
						raise Exception("Invalid og_base_dir! Cannot convert from legacy!")
					e['files'][k] = fn.replace(self.og_base, '').lstrip('/\\')
			if e['type'] == 'Comment':
				e['parent'] = e['id']  # Previous versions used Parent ID instead of their own.
				print("Searching for Comment: %s" % e['id'], end='\r', flush=True)
				com = self.find_comment(e)
				if not com:
					print('Could not match old Comment; Will re-download. [%s]' % e['id'])
					self.failed.append(FailedPost(e['id'], e['title'], e['files'], "Comment ID could not be converted from parent"))
					continue
				e['id'] = com.name
			yield PendingPost(e['id'], e['files'], e['source_alias'], title=e['title'], reddit_ele=com)


class SQLDBManifest:
	def __init__(self, sql_path):
		self.sql = sql_path
		self.posts = {}

	def convert(self):
		conn = sqlite3.connect(self.sql)
		query = conn.execute('''
			SELECT p.id, p.title, p.source_alias, u.url, u.file_path FROM urls u
			LEFT JOIN posts p ON u.post_id = p.id
			ORDER BY p.id
		''')
		names = [description[0] for description in query.description]
		for row in query:
			p = dict(zip(names, row))
			if p['id'] not in self.posts:
				self.posts[p['id']] = {
					'reddit_id': p['id'],
					'files': {},
					'source': p['source_alias'],
					'title': p['title']
				}
			self.posts[p['id']]['files'][p['url']] = p['file_path']
		conn.close()
		for k, v in self.posts.items():
			yield PendingPost(**v)


class Converter:
	def __init__(self, new_save_base=None, settings_file=None, manifest_gz=None, og_base_dir_path=None, gz_base_dir_name=None, sqlite_path=None):
		self.posts = {}
		self.new_save_base = os.path.abspath(new_save_base)
		self.settings_file = settings_file
		self.manifest_gz = manifest_gz
		self.og_base_dir_path = os.path.abspath(og_base_dir_path)
		self.gz_base_dir_name = gz_base_dir_name
		self.sqlite_path = os.path.abspath(sqlite_path)
		if stringutil.normalize_file(self.new_save_base) == stringutil.normalize_file(og_base_dir_path):
			raise Exception("ERROR: You must specify a NEW directory to save the converted Posts!")
		# internal:
		self.session = None
		self.gz = None
		self.sqlite = None
		self.failures = []

	def start(self):
		os.makedirs(self.new_save_base, exist_ok=True)
		if not settings.load(self.settings_file):
			raise Exception("You must provide a valid settings.json file!")
		settings.put('output.base_dir', self.new_save_base)
		sql.init_from_settings()
		self.session = sql.session()
		print("Scanning legacy posts...")
		self.scan()
		print("Found %s elements total." % len(self.posts.keys()))
		self.process_posts()
		self.session.commit()
		print("Processed:", len(self.posts), "Posts.")
		print("Failed to convert %s Posts." % len(self.failures))
		outfile = os.path.join(self.new_save_base, 'failed_conversion_posts.json')
		with open(outfile, 'w') as o:
			o.write(json.dumps(self.failures, indent=4, sort_keys=True, separators=(',', ': ')))
			print("Saved a list of failed posts to", outfile, ', be sure to check these before deleting anything!')

	def scan(self):
		if self.manifest_gz:
			print("Loading manifest.gz data...")
			self.gz = GZManifest(self.manifest_gz, self.gz_base_dir_name)
			for _e in self.gz.convert():
				self.posts[_e.reddit_id] = _e
			print("Failed GZ conversions:", len(self.gz.failed))
			self.failures.extend(self.gz.failed)
			print("Found %s elements from GZ Archive." % len(self.posts))
		if self.sqlite_path:
			self.sqlite = SQLDBManifest(self.sqlite_path)
			for _e in self.sqlite.convert():
				if _e.reddit_id not in self.posts:
					self.posts[_e.reddit_id] = _e
				else:
					of = self.posts[_e.reddit_id].files
					for k, v in _e.files.items():
						if k not in of or not of[k]:
							self.posts[_e.reddit_id].files[k] = v
							print('Merged over old/missing file from gz archive: ', k, '->', v)
		self.failures = list(filter(lambda _f: _f.reddit_id not in self.posts, self.failures))

	def process_posts(self):
		""" Iterate through all the located PendingPosts, and process them. """
		for idx, pend in enumerate(self.posts.values()):
			r = pend.ele
			if not r:
				try:
					if pend.reddit_id.startswith('t3_'):
						print("Searching for Submission:", pend.reddit_id)
						r = RedditElement(rd.get_submission(pend.reddit_id))
					else:
						print("Searching for Comment:", pend.reddit_id)
						r = RedditElement(rd.get_comment(pend.reddit_id))
				except Exception as ex:
					print(ex)
					self.failures.append(FailedPost(pend.reddit_id, pend.title, pend.files, reason="Error parsing: %s" % ex))
					continue
			r.source_alias = pend.source + '-imported'
			post = self.session.query(sql.Post).filter(sql.Post.reddit_id == r.id).first()
			if not post:
				post = sql.Post.convert_element_to_post(r)
			self.find_missing_files(pending=pend, post=post)
			total = len(self.posts.keys())
			print("\n\nFinished Post: %s/%s" % (idx, total), ' :: ', "%s%%" % round((idx/total)*100, 2))

	def find_missing_files(self, pending=None, post=None):
		""" Accepts a PendingPost object and a SQL Post object, and processes the pending Files & URLs into the DB. """
		for url, file in pending.files.items():
			print(url, file)
			existing_url = self.session.query(sql.URL).filter(sql.URL.address == url).first()
			if existing_url and existing_url.processed and not existing_url.failed:
				continue  # URL already exists & is processed properly.
			if not file or any(file.endswith(bn) for bn in ['unknownvideo', 'unknown_video']):
				print("Found incomplete URL:", url, file)
				self.build_missing_files(files=[None], post=post, sql_url=existing_url, uri=url)
				continue
			files = self.split_file(file)  # Split this file/dir into a list of all file paths contained within.
			print('\tParsed Files:', files)
			if not files:
				files = [None]
			print("Found missing URL:", url, existing_url)
			self.build_missing_files(files=files, post=post, sql_url=existing_url, uri=url)

	def build_missing_files(self, files, post, sql_url, uri):
		""" Accepts a list of files, and the URL they came from.
			Builds the SQL representation & copies the file.

			This function will create extra URL + File SQL objects to account for every file in the given list.
			If the sql_url object is already in the DB, it will add the file to that object first.
		"""
		album_key = None if len(files) <= 1 else str(uuid.uuid4())
		for idx, file_path in enumerate(files):
			if not sql_url:
				sql_url = sql.URL.make_url(address=uri, post=post, album_key=album_key, album_order=idx)
			has_file = bool(file_path)
			sql_url.failed = not has_file
			sql_url.processed = has_file
			sql_url.last_handler = 'legacy-importer'
			if not has_file:
				sql_url.failure_reason = 'Unable to convert from legacy.'
			self.session.add(sql_url)
			post.urls.append(sql_url)
			file = self.create_url_file(sql_url=sql_url, sql_post=post, album_size=len(files), downloaded=has_file)
			print("CREATED:", sql_url, file)
			if has_file:
				file.path = self.copy_file(file_path, file.path)
			self.session.commit()
			sql_url = None

	def copy_file(self, og_file_path, relative_path):
		""" Copy the file at the given absolute path into the relative path given, relative to the base_dir. """
		rf = rel_file.SanitizedRelFile(base=self.new_save_base, file_path=relative_path)
		rf.mkdirs()
		rf.set_ext(og_file_path.split('.')[-1].strip())
		print("\t\tRelFile:", rf)
		shutil.copyfile(og_file_path, rf.absolute())
		return rf.relative()

	def split_file(self, filename):
		""" Splits the given relative filename into a list of all files within the file/directory path. """
		path = os.path.join(self.og_base_dir_path, filename)
		ret = []
		if os.path.isfile(path):
			ret.append(path)
		elif os.path.isdir(path):
			ret.extend(os.path.join(path, p) for p in os.listdir(path) if not os.path.isdir(p))
		return [stringutil.normalize_file(_r) for _r in ret if _r]

	def create_url_file(self, sql_url, sql_post, album_size, downloaded=True):
		""" Creates a SQL File object for the given SQL URL & Post. """
		if sql_url.file:
			return sql_url.file
		filename = name_generator.choose_file_name(url=sql_url, post=sql_post, session=self.session, album_size=album_size)
		file = sql.File(
			path=filename
		)
		self.session.add(file)
		sql_url.file = file
		file.downloaded = downloaded
		return file


def arg_or_input(arg, prompt):
	return arg if arg else console.string(prompt=prompt)


if __name__ == '__main__':
	opts = {
		'new_save_base': arg_or_input(args.new_save_dir, "Enter the new directory (absolute) for RMD to save in"),
		'settings_file': arg_or_input(args.settings, "Enter the absolute path to your settings.json file"),
		'og_base_dir_path': arg_or_input(args.og_base_dir_path, "Enter the absolute path to the directory RMD was saving in"),
	}
	path_gz = os.path.join(opts['og_base_dir_path'], 'Manifest.json.gz')
	path_sql = os.path.join(opts['og_base_dir_path'], 'manifest.sqldb')
	check_gz = os.path.isfile(path_gz)
	check_sql = os.path.isfile(path_sql)
	if check_gz and console.confirm('Detected a "Manifest.json.gz" file (from RMD <2.0) - do you want to convert this?', default=True):
		opts['manifest_gz'] = os.path.abspath(path_gz)
		opts['gz_base_dir_name'] = arg_or_input(args.og_base_dir_name, "Enter the EXACT path (exactly as is written!) that RMD used in settings.json -> 'base_dir'")
	if check_sql and console.confirm('Detected a "manifest.sqldb" file (from RMD <3.0) - do you want to convert this?', default=True):
		opts['sqlite_path'] = os.path.abspath(path_sql)

	if all(mf not in opts for mf in ['manifest_gz', 'sqlite_path']):
		print('No legacy manifests were located! Nothing to convert.')
		sys.exit(1)
	converter = Converter(**opts)
	converter.start()
