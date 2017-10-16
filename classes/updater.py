import sys
from hashlib import sha1
import os
import json


class Updater(object):
	""" Uses the supplied github url to sync the given directory to the contents of the git folder. """
	def __init__(self, target_dir, url, skip_pauses = False):
		self.dir = target_dir
		self.url = url
		self.skip_pauses = skip_pauses
		self.yes_all = self.skip_pauses
		self.url_append = '?'
		if 'GITHUB_CLIENT_ID' in os.environ:
			if '?' in self.url:
				self.url_append = '&'
			self.url_append += ('client_id=%s&client_secret=%s' % (os.environ['GITHUB_CLIENT_ID'], os.environ['GITHUB_CLIENT_SECRET']) )
			print("Using custom github auth.")
			self.url += self.url_append
	#
	
	def pip_update(self):
		""" Uses the pip module to update all required libs. """
		print('Launching updater...')
		print('Make sure to visit https://travis-ci.org/shadowmoose/RedditDownloader and make sure that the latest build is passing!')
		if not self.skip_pauses:
			if 'c' in input('Press enter to continue (enter "c" to abort): ').lower():
				print('Aborted update')
				sys.exit(1)
			print()
		if os.path.isfile('./requirements.txt'):
			# I don't really like calling this type of thing, because it can easily fail without root access when it builds.
			# However, it's a very straightforward way to let people automatically update the ever-shifting packages like YTDL
			print("Attempting to automatically update required external packages. May require root to work properly on some setups.")
			import pip
			pip.main(["install", "--upgrade", "-r","requirements.txt"])
			
			print("Completed package update.")
		else:
			print("Couldn't locate a requirements.txt file. Cannot update dependencies.")
	#
	
	def run(self):
		"""
		Launch the updater
		"""
		print('== Updating... ==')
		self.pip_update()
		print()

		import requests # Wait to bring in requests lib until it's been updated.
		# requests allows for "#.get().json()", but not all target libs support that.
		response = requests.get(self.url, headers = {'User-Agent': 'RedditDownloader-HandlerUpdater'})
		print('Github Response: %i' % response.status_code)
		files = json.loads(response.text)
		if self.yes_all:
			print(files)
		
		local_files = []
		
		for ff in os.listdir(self.dir):
			if ff == '__init__.py' or ff[-3:] != '.py':
				continue
			path = os.path.join(self.dir, ff)
			file_hash = self.file_hash(path)
			local_files.append(ff)
			
			found = False
			for cf in files:
				if cf['name'] == ff:
					found = True
					if cf['sha'] != file_hash:
						print('+Handler: %s is outdated: [%s] => [%s]' % (ff.replace('.py',''), file_hash, cf['sha']) )
						self.download(cf['download_url'], path)
						if self.file_hash(path) != cf['sha']:
							print('\tError: Handler file has mismatch!')
							sys.exit(12)
			if not found:
				# Old file that no longer exists on server.
				print('-Handler "%s" has been deprecated!' % ff)
				prompt = ''
				if not self.yes_all:
					prompt = input('\tWould you like to delete this old handler? (y/n/yes-all): ').lower()
					if 'yes-all' in prompt:
						self.yes_all = True
				
				if self.yes_all or 'y' in prompt:
					print('\tFile "%s" deleted.' % ff)
					os.remove(path)
				else:
					print('\tIgnoring file...')
		# Finally, check for new files from server.
		for o in files:
			if o['name'] not in local_files:
				print('+New Handler: %s' % o['name'].replace('.py','') )
				self.download(o['download_url'], os.path.join(self.dir, o['name']))
				if self.file_hash(os.path.join(self.dir, o['name'])) != o['sha']:
					print('\tError: Handler file has mismatch!')
					sys.exit(12)
		print('Update Complete.')
		print('=================')
	#
	
	def download(self, url, path):
		print("\tDownloading new source: %s" % url)
		import requests
		response = requests.get(url,  headers = {'User-Agent': 'RedditDownloader-HandlerUpdater'}, stream=True)
		
		with open(path, "wb") as f:
			f.write(response.content)
	#
	
	def file_hash(self, path):
		""" Get the string hash of this filepath. """
		with open(path, 'r') as f:
			data=f.read()
		return self.git_hash(data)
	#
	
	
	def git_hash(self, data):
		""" Generate the string hash of the given data (string), following how Git does it. """
		sh = sha1()
		sh.update( ("blob %u\0" % len(data) ).encode('utf-8') )
		sh.update(data.encode('utf-8') )
		return sh.hexdigest()
	#
