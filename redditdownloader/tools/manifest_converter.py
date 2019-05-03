import gzip
import json
import argparse
from static import settings
from static import praw_wrapper as rd
from static import stringutil
from processing.wrappers.redditelement import RedditElement
import sql
import os
import uuid
from processing import name_generator
from processing.wrappers import rel_file
import shutil
from static import console


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
	def __init__(self, reddit, files, source, title, reddit_ele=None):
		self.reddit = reddit
		self.title = title
		self.files = files
		self.source = source
		self.ele = RedditElement(reddit_ele) if reddit_ele else None

	def __str__(self):
		return "<Post ID: %s, Files: %s, Ele: %s>" % (self.reddit, self.files, True if self.ele else False)


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


class Converter:
	def __init__(self, new_save_base, settings_file, manifest_gz, og_base_dir_path, og_base_dir_name):
		self.posts = {}
		self.new_save_base = os.path.abspath(new_save_base)
		self.settings_file = settings_file
		self.manifest_gz = manifest_gz
		self.og_base_dir_path = os.path.abspath(og_base_dir_path)
		self.og_base_dir_name = og_base_dir_name
		if stringutil.normalize_file(self.new_save_base) == stringutil.normalize_file(og_base_dir_path):
			raise Exception("ERROR: You must specify a NEW directory to save the converted Posts!")
		# internal:
		self.session = None
		self.gz = None
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
		print("Found %s elements." % len(self.posts.keys()))
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
			self.gz = GZManifest(self.manifest_gz, self.og_base_dir_name)
			for _e in self.gz.convert():
				self.posts[_e.reddit] = _e
			print("Failed GZ conversions:", len(self.gz.failed))
			self.failures.extend(self.gz.failed)

	def process_posts(self):
		""" Iterate through all the located PendingPosts, and process them. """
		for idx, pend in enumerate(self.posts.values()):
			r = pend.ele
			if not r:
				try:
					print("Searching for post:", pend.reddit)
					r = RedditElement(rd.get_submission(pend.reddit))
				except Exception as ex:
					print(ex)
					self.failures.append(FailedPost(pend.reddit, pend.title, pend.files, reason="Error parsing: %s" % ex))
					continue
			r.source_alias = pend.source + '-imported'
			post = self.session.query(sql.Post).filter(sql.Post.reddit_id == r.id).first()
			if not post:
				post = sql.Post.convert_element_to_post(r)
			self.find_missing_files(pending=pend, post=post)
			total = len(self.posts.keys())
			print("Finished Post: %s/%s" % (idx, total), ' :: ', "%s%%" % round((idx/total)*100, 2))

	def find_missing_files(self, pending=None, post=None):
		""" Accepts a PendingPost object and a SQL Post object, and processes the pending Files & URLs into the DB. """
		for url, file in pending.files.items():
			print(url, file)
			if not file:
				continue
			files = self.split_file(file)  # Split this file/dir into a list of all file paths contained within.
			print('\tParsed:', files)
			if not files:
				continue
			finished = self.session.query(sql.URL).filter(sql.URL.address == url).first()
			if finished and finished.processed and not finished.failed:
				continue  # URL already exists & is processed properly.
			print("Found missing URL:", url, finished)
			self.build_missing_files(files=files, post=post, sql_url=finished, uri=url)

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
			sql_url.failed = False
			sql_url.processed = True
			sql_url.last_handler = 'legacy-importer'
			self.session.add(sql_url)
			post.urls.append(sql_url)
			file = self.create_url_file(sql_url=sql_url, sql_post=post, album_size=len(files))
			print("CREATED:", sql_url, file)
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

	def create_url_file(self, sql_url, sql_post, album_size):
		""" Creates a SQL File object for the given SQL URL & Post. """
		if sql_url.file:
			return sql_url.file
		filename = name_generator.choose_file_name(url=sql_url, post=sql_post, session=self.session, album_size=album_size)
		file = sql.File(
			path=filename
		)
		self.session.add(file)
		sql_url.file = file
		file.downloaded = True
		return file


def arg_or_input(arg, prompt):
	return arg if arg else console.string(prompt=prompt)


if __name__ == '__main__':
	converter = Converter(
		new_save_base=arg_or_input(args.new_save_dir, "Enter the new directory (absolute) for RMD to save in"),
		settings_file=arg_or_input(args.settings, "Enter the absolute path to your settings.json file"),
		manifest_gz=arg_or_input(args.manifest_gz, "Enter the absolute path to the legacy Manifest.json.gz file, or leave blank"),
		og_base_dir_path=arg_or_input(args.og_base_dir_path, "Enter the absolute path to the directory RMD was saving in"),
		og_base_dir_name=arg_or_input(args.og_base_dir_name, "Enter the EXACT path (exactly as is in the file!) that RMD used in settings.json -> 'base_dir'")
	)
	converter.start()
