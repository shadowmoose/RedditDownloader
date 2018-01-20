import os
from hashlib import sha1
import pip
import shutil

try:
	import requests
except ImportError:
	print('Bootstrapping "requests" package... ')
	pip.main(["install", "--upgrade", "requests"])
	import requests

class Updater:
	def __init__(self, author, repo, version, skip_prompt=False):
		self._author = author
		self._repo = repo
		self._version = version
		self._client_auth = ''
		self._file_tree = None
		self._skip_prompt = skip_prompt
		if 'GITHUB_CLIENT_ID' in os.environ:
			# Support custom environment variables to bypass github's unathenticated request throttling.
			# This is mostly done for testing services like TravisCI, who get throttled constantly without auth.
			self._client_auth = 'client_id=%s&client_secret=%s' % (os.environ['GITHUB_CLIENT_ID'], os.environ['GITHUB_CLIENT_SECRET'])
			print("Using custom github auth.")


	def run(self):
		""" Launches the updater process, and prompts to clean up old files if remove_old is true. """
		self._update_from_git()
		self._pip_update() # call second so the requirements file is updated in advance.


	def _get_latest_file_tree(self):
		""" Connect to Github and pull the latest information manifest for the repository. Caches result. """
		if self._file_tree is not None:
			return self._file_tree
		self._file_tree = []

		if '-' in str(self._version):
			print('Standalone versions cannot auto-update!')
			print('You are currently running Standalone version %s' % self._version)
			print('Go manually update from: https://github.com/%s/%s/releases' % (self._author, self._repo))
			return []

		print("Checking for new version...")
		print("If an error occurs that prevents updating, please check manually at https://github.com/%s/%s" % (self._author, self._repo))
		n_dat = requests.get('https://api.github.com/repos/%s/%s/releases/latest?%s' % (self._author, self._repo, self._client_auth)).json()
		newest_version = n_dat['tag_name']
		update_text = n_dat['body'].replace('[','').replace(']','')
		update_title = n_dat['name']

		if '-' in newest_version or float(self._version) >= float(newest_version):
			print("\t+Up to date! (Version: %s)" % self._version)
			return self._file_tree
		print("\nCurrently on version: %s" % self._version)
		print("Found new version: %s! \"%s\"" % (newest_version, update_title))
		print("\n============ Update Text ============\n\n%s\n\n=====================================" % update_text)
		if not self._skip_prompt:
			try:
				input("- Press Enter to continue, ctrl+c to cancel -")
			except (EOFError, KeyboardInterrupt):
				import sys
				print('\n\nClosing instead of updating.')
				sys.exit(0)
		print("\t+Pulling file deltas...")

		data = requests.get('https://api.github.com/repos/%s/%s/compare/%s...%s?%s' %
							(self._author, self._repo, self._version, newest_version, self._client_auth)).json()
		#  https://api.github.com/repos/shadowmoose/RedditDownloader/compare/1.0...1.1
		self._file_tree = data['files']
		return self._file_tree


	def _update_from_git(self):
		""" Pull file deltas from Github and process update. """
		deltas = self._get_latest_file_tree()
		print()
		if len(deltas)==0:
			print('All files up to date!')
			return
		else:
			print("Found %i files to update:" % len(deltas))

		for f in deltas:
			status = f['status']
			f_name = f['filename']
			f_url  = f['raw_url']
			f_sha  = f['sha']
			f_local = os.path.normpath(os.path.join('./', f_name))
			local_sha = self._file_hash(f_local)

			print('\t>> %s | %s' % (f_local, status))
			if status == 'modified' or status == 'added':
				if local_sha != f_sha:
					print("\t\t+Downloading [%s] from [%s]..." % (f_local, f_url))
					self._download(f_url, f_local, sha_hash=f_sha)
				else:
					print('\t\tLOCAL OK | %s [%s]' % (f_local, local_sha))
			elif status == 'renamed':
				prev_path = os.path.normpath(os.path.join('./', f['previous_filename']))
				if local_sha == f_sha:
					print("\t\tFile moved already.")
					continue
				if os.path.exists(f_local):
					self._delete_file(f_local)
				if os.path.exists(prev_path):
					self.make_parent_dirs(f_local)
					os.rename(prev_path, f_local)
					print('\t\t+Moved file.')
				else:
					self._download(f_url, f_local, sha_hash=f_sha)
					print("\t\t+Couldn't find original, so downloaded file.")
			elif status == 'removed':
				if os.path.exists(f_local):
					print('\t\t-Removed file %s' % f_local)
					self._delete_file(f_local)
				else:
					print('\t\tRemoved already.')
			else:
				print("!!! ERROR: Unknown File Delta: [%s] !!!" % status)
		print("\tFile update complete.\n")


	def _delete_file(self, path):
		""" Deletes whatever file object is at the given path. """
		print("Deleting [%s]" % path)
		if not os.path.exists(path):
			print("File %s does not exist for deletion." % path)
			return False
		if os.path.isfile(path):
			return os.remove(path)
		elif os.path.isdir(path):
			return shutil.rmtree(path, ignore_errors=True)


	def _file_hash(self, path):
		""" Get the string hash of this filepath. """
		if not os.path.exists(path):
			return None
		try:
			with open(path, 'r') as f:
				data=f.read()
			return self._git_hash(data)
		except FileNotFoundError as fnf:
			print("Oops, a local file doesn't exist that we were expecting to check!")
			print("Assuming it's gone. This is probably correctable.")
			return None


	def _git_hash(self, data):
		""" Generate the string hash of the given data (string), following how Git does it. """
		sh = sha1()
		sh.update( ("blob %u\0" % len(data) ).encode('utf-8') )
		sh.update(data.encode('utf-8') )
		return sh.hexdigest()


	def _download(self, url, path, sha_hash=None):
		""" Downloads the target file. If sha_hash is set, it will validate the download with the provided hash. """
		self.make_parent_dirs(path)
		response = requests.get(url,  headers = {'User-Agent': 'RedditDownloader-HandlerUpdater'}, stream=True)

		with open(path, "wb") as f:
			f.write(response.content)

		if sha_hash:
			assert sha_hash == self._file_hash(path)


	def make_parent_dirs(self, path):
		""" If it does not exist, create the parent directory (and subdirs as needed) to this path. """
		if not os.path.exists(os.path.dirname(path)) and os.path.dirname(path) != '':
			try:
				os.makedirs(os.path.dirname(path))
				return True
			except OSError as exc: # Guard against race condition
				import errno
				if exc.errno != errno.EEXIST:
					raise
		return False


	def _pip_update(self):
		""" Uses the pip module to update all required libs. """
		print("\nAttempting to automatically update required external packages...")
		print("(THIS MAY REQUIRE ROOT/ADMIN TO WORK PROPERLY ON SOME SETUPS)\n\n")
		if os.path.isfile('./requirements.txt'):
			# I don't really like calling this type of thing, because it can fail without root access when it builds.
			# However, it's a very simple way to let people automatically update the ever-shifting packages like YTDL
			try:
				val = pip.main(["install", "--upgrade", "-r","requirements.txt"])
				if val == 2:
					raise PermissionError
				print("\t+Completed package update.")
			except PermissionError:
				print("\nERROR: Could not auto-update your packages - This script lacks the permissions to do so!")
				print("For package updating, Make sure you're launching this script from an console running as Administrator or Root!")
		else:
			print("\t! Couldn't locate a requirements.txt file. Cannot update dependencies.")
		#
