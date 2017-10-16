import requests
import os
from hashlib import sha1
import pip


class Updater:
	def __init__(self, author, repo, branch):
		self._author = author
		self._repo = repo
		self._branch = branch
		self._client_auth = '?'
		self._file_tree = None
		if 'GITHUB_CLIENT_ID' in os.environ:
			# Support custom environment variables to bypass github's unathenticated request throttling.
			self._client_auth = 'client_id=%s&client_secret=%s' % (os.environ['GITHUB_CLIENT_ID'], os.environ['GITHUB_CLIENT_SECRET'])
			print("Using custom github auth.")
		if 'TRAVIS_BRANCH' in os.environ:
			self._branch = os.environ['TRAVIS_BRANCH']
			print('Using custom TravisCI branch: %s' % self._branch)


	def run(self, prompt_remove_old = False):
		""" Launches the updater process, and prompts to clean up old files if remove_old is true. """
		self._pip_update()
		self._check_missing_updated()
		if prompt_remove_old:
			self._clean_existing_files()

	def _get_latest_manifest(self):
		""" Connect to Github and pull the latest information manifest for the repository. """
		data = requests.get('https://api.github.com/repos/%s/%s/git/trees/%s?recursive=1&%s' %
							(self._author, self._repo, self._branch, self._client_auth)).json()
		#  https://api.github.com/repos/shadowmoose/RedditDownloader/git/trees/master?recursive=1
		return data


	def _get_latest_file_tree(self):
		""" Pulls the latest file tree off git, and caches it. """
		if self._file_tree is None:
			self._file_tree = self._get_latest_manifest()['tree']
		return self._file_tree


	def _file_hash(self, path):
		""" Get the string hash of this filepath. """
		if not os.path.exists(path):
			return None
		with open(path, 'r') as f:
			data=f.read()
		return self._git_hash(data)


	def _git_hash(self, data):
		""" Generate the string hash of the given data (string), following how Git does it. """
		sh = sha1()
		sh.update( ("blob %u\0" % len(data) ).encode('utf-8') )
		sh.update(data.encode('utf-8') )
		return sh.hexdigest()


	def _check_missing_updated(self):
		""" Locate and queue all missing/updated files from the repository. """
		tree = self._get_latest_file_tree()
		print("Checking for file updates...")
		for f in tree:
			file = os.path.normpath(os.path.join('./', f['path'])) # The relative path to the file.
			f_type = f['type'] # What this file represents
			sha = f['sha']   # The git hash of this file

			if f_type == 'tree':
				if not os.path.exists(file):
					os.makedirs(file, exist_ok=True)
				continue # Skip Directories

			local_sha = self._file_hash(file)
			# https://raw.githubusercontent.com/shadowmoose/RedditDownloader/master/.travis.yml
			download_url = 'https://raw.githubusercontent.com/%s/%s/%s/%s' % (
				self._author, self._repo, self._branch, f['path']
			)
			if local_sha != sha:
				print("\tUpdating file [%s] from [%s]..." % (file, download_url))
				self._download(download_url, file)
			else:
				print("\tOK | %s" % file)


	def _clean_existing_files(self):
		""" Cleans up - after prompting for each one - files that no longer exist in the repo. """
		repo_files = self._get_latest_file_tree()
		print("Scanning existing files for deletions...")
		for ff in os.listdir('./'):
			for rf in repo_files:
				if rf['path'] == ff:
					print("\tEXISTS | [%s]" % ff)
					break
			else:
				print("\tFile [%s] not found in recent manifest." % ff)
				self._delete_file(ff)


	def _delete_file(self, file_name):
		""" Prompts the user and then removes the given file. """
		print('-The file [%s] is not part of the latest build.' % file_name)

		if 'y' in input('\tWould you like to delete this old file? (y/n): ').lower():
			print('\tFile "%s" deleted.' % file_name)
			os.remove(file_name)
		else:
			print('\tIgnoring file...')


	def _download(self, url, path):
		""" Downloads the target file. """
		response = requests.get(url,  headers = {'User-Agent': 'RedditDownloader-HandlerUpdater'}, stream=True)

		with open(path, "wb") as f:
			f.write(response.content)


	def _pip_update(self):
		""" Uses the pip module to update all required libs. """
		print("Attempting package update...")
		if os.path.isfile('./requirements.txt'):
			# I don't really like calling this type of thing, because it can easily fail without root access when it builds.
			# However, it's a very straightforward way to let people automatically update the ever-shifting packages like YTDL
			print("Attempting to automatically update required external packages. May require root to work properly on some setups.")
			pip.main(["install", "--upgrade", "-r","requirements.txt"])
			print("Completed package update.")
		else:
			print("Couldn't locate a requirements.txt file. Cannot update dependencies.")
		#