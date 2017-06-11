import sys
from hashlib import sha1
import requests;
import os;
import json;


class Updater(object):
	""" Uses the supplied github url to sync the given directory to the contents of the git folder. """
	def __init__(self, target_dir, url, skip_pauses = False):
		self.dir = target_dir;
		self.url = url;
		self.skip_pauses = skip_pauses;
		self.url_append = '?';
		if 'GITHUB_CLIENT_ID' in os.environ:
			if '?' in self.url:
				self.url_append = '&'
			self.url_append += ('client_id=%s&client_secret=%s' % (os.environ['GITHUB_CLIENT_ID'], os.environ['GITHUB_CLIENT_SECRET']) );
			print("Using custom github auth.");
			self.url += self.url_append;
	#
	
	
	def run(self):
		print('== Updating... ==');
		self.yes_all = self.skip_pauses;
		# requests allows for "#.get().json()", but not all target libs support that.
		response = requests.get(self.url, headers = {'User-Agent': 'RedditDownloader-HandlerUpdater'});
		print('Github Response: %i' % response.status_code)
		files = json.loads(response.text);
		if self.yes_all:
			print(files);
		
		local_files = [];
		
		for ff in os.listdir(self.dir):
			if ff == '__init__.py' or ff[-3:] != '.py':
				continue;
			path = os.path.join(self.dir, ff)
			hash = self.file_hash(path);
			local_files.append(ff);
			
			found = False;
			for cf in files:
				if cf['name'] == ff:
					found = True;
					if cf['sha'] != hash:
						print('+Handler: %s is outdated: [%s] => [%s]' % (ff.replace('.py',''), hash, cf['sha']) )
						self.download(cf['download_url'], path);
						if self.file_hash(path) != cf['sha']:
							print('\tError: Handler file has mismatch!');
							sys.exit(12);
			if not found:
				# Old file that no longer exists on server.
				print('-Handler "%s" has been deprecated!' % ff);
				prompt = '';
				if not self.yes_all:
					prompt = input('\tWould you like to delete this old handler? (y/n/yes-all): ').lower();
					if 'yes-all' in prompt:
						self.yes_all = True;
				
				if self.yes_all or 'y' in prompt:
					print('\tFile "%s" deleted.' % ff);
					os.remove(path);
				else:
					print('\tIgnoring file...')
		# Finally, check for new files from server.
		for o in files:
			if o['name'] not in local_files:
				print('+New Handler: %s' % o['name'].replace('.py','') )
				self.download(o['download_url'], os.path.join(self.dir, o['name']))
				if self.file_hash(os.path.join(self.dir, o['name'])) != o['sha']:
					print('\tError: Handler file has mismatch!');
					sys.exit(12);
		print('Update Complete.')
		print('=================')
	#
	
	def download(self, url, path):
		print("\tDownloading new source: %s" % url);
		response = requests.get(url,  headers = {'User-Agent': 'RedditDownloader-HandlerUpdater'}, stream=True)
		total_length = response.headers.get('content-length')
		
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
