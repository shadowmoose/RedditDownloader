import argparse
import sys;
parser = argparse.ArgumentParser(description="Save all Media Upvoted & Saved on Reddit")
parser.add_argument("--settings", help="path to custom Settings file")
parser.add_argument("-t", "--test", help="launch in Test Mode. Only used for Travis testing.",action="store_true")
parser.add_argument("--username", help="Account Username")
parser.add_argument("--password", help="Account password")
parser.add_argument("--c_id", help="Reddit Client ID")
parser.add_argument("--c_secret", help="Reddit Client Secret")
parser.add_argument("--agent", help="String to use for User-Agent")
args = parser.parse_args()

sys.path.insert(0, './handlers')
sys.path.insert(0, './classes')

import praw;
from pprint import pformat
import os;
import re;
import string;
from stringutil import StringUtil;
from redditelement import RedditElement as RE;
import json;
import time;
from settings import Settings;

handlers = [];
for module in os.listdir('./handlers/'):
	if module == '__init__.py' or module[-3:] != '.py':
		continue
	lib = __import__(module[:-3], locals(), globals())
	handlers.append(lib);
#
handlers.sort(key=lambda x: x.order, reverse=False);
print("Loaded handlers: ", ', '.join([x.tag for x in handlers]) );


def out(obj):
	""" Prints out the given object in the shitty format the Windows Charmap supports. """
	if isinstance(obj, str):
		print(obj.encode('ascii', 'ignore').decode('ascii') );
	elif isinstance(obj, (int, float, complex)):
		print(obj);
	else:
		print(pformat(vars(obj)).encode('ascii', 'ignore').decode('ascii') );
#

class Scraper(object):
	
	def __init__(self, settings_file=None, override_login=None):
		if not settings_file:
			settings_file = './settings.json'
		self.settings = Settings(settings_file, override_login==None );
		self.reddit = None;
		self.me = None;
		self.output = self.settings.get('output', {'base_dir':'./download/', 'subdir_pattern':'/[subreddit]/', 'file_name_pattern':'[title] - ([author])'}, True);
		self.download_dir = self.output['base_dir'];
		self.manifest_file = self.download_dir+'/manifest.json';
		
		self.all_reddit = [];# List of all posts we've liked/saved. Stored initially to avoid timeouts.
		self.elements = [];# List of redditelement wrappers
		self.used_filenames = [];# Keep a local list of used filenames, just for ease of lookup.
		
		
		
		# Authenticate and prepare to scan:
		info = {};
		if not override_login:
			info = self.settings.get('auth');
		else:
			info = override_login;
			print("Using custom login.");
		if not info:
			print('Error loading authentication information!');
			return;
		self.settings.set('last_started', time.time());
		
		print("Authenticating via OAuth...");
		self.reddit = praw.Reddit(client_id=info['client_id'], client_secret=info['client_secret'],password=info['password'], user_agent=info['user_agent'], username=info['username']);
		self.me = self.reddit.user.me();
		print("Authenticated as [%s]" % self.me.name)
	#
	
	
	def scan(self):
		''' Grab all saved Comments and Posts in advance, called automaticall by run(). '''
		if not self.me:
			return;
		print('Loading Saved Comments & Posts...');
		for saved in self.me.saved(limit=None):
			if saved not in self.all_reddit:
				self.all_reddit.append(saved);
		print('Loading Upvoted Comments & Posts...');
		for upvoted in self.me.upvoted(limit=None):
			if upvoted not in self.all_reddit:
				self.all_reddit.append(upvoted);
	#
	
	
	def run(self):
		''' Run through all saved/upvoted Comments and Posts, and process them. '''
		self.scan();
		try:
			for saved in self.all_reddit:
				print('%i/%i: ' % (len(self.elements)+1, len(self.all_reddit) ), end='');
				re = RE(saved);
				self.process_ele(re);
				self.elements.append(re);
				print();
		except KeyboardInterrupt:
			print("Interrupted by User.");
		self.settings.set('last_finished', time.time() );
		self.build_manifest();
	#
	
	
	
	def build_manifest(self):
		if self.settings.get('build_manifest', True, True):
			with open(self.manifest_file, 'w') as outfile:
				obj = {
					'@meta':{
						'version': 1.0,
						'timestamp': time.time(),
						'base_dir' : self.download_dir,
						'finished': (len(self.elements) == len(self.all_reddit)),
						'number_completed': len(self.elements),
						'number_found' : len(self.all_reddit),
					},
					'elements':[x.to_obj() for x in self.elements],
				};
				json.dump(obj, outfile, sort_keys=True, indent=4, separators=(',', ': '))
			
			failed = False;
			for el in self.elements:
				for f,k in el.get_completed_files().items():
					if k == False:
						if not failed:
							print('============================ FAILED URLS ============================');
							failed = True;
						print("\t[%s] [%s]" % (f, el.id) )
			if failed:
				print('=====================================================================');
			print("Built manifest.");
		else:
			print('Manifest disabled by settings.')
	#
	
	
	def filename(self, filename):
		''' Format the givne string into an acceptable filename. '''
		valid_chars = "-_.() %s%s[]" % (string.ascii_letters, string.digits)
		return ''.join(c for c in filename if c in valid_chars);
	#
	
	def insert_vars(self, str_path, ele):
		''' Replace the [tagged] ele fields in the given string. '''
		for k,v in ele.to_obj().items():
			str_path = str_path.replace('[%s]' % str(k), self.filename(str(v)) )
		return str_path.replace('\\', '/').replace("//", '/');
	
	def process_ele(self, re):
		'''  Accepts a RedditElement of Post/Comment details, then runs through the Handlers loaded from the other directory, attempting to download the url.  '''
		out("[%s](%s): %s" % (re.type, re.subreddit, re.title) );
		for url in re.get_urls():
			out("\tProcessing URL: %s" % url);
			existing = False;
			# Check if we've handled this URL before, and pass the file location if we have.
			for e in self.elements:
				if url in e.get_completed_files():
					files = e.get_completed_files();
					re.add_file(url, files[url]);
					existing = True;
					break;
			if existing:
				print("\t\t+URL already taken care of.")
				continue;
			
			dir_pattern  = self.download_dir + self.output['subdir_pattern']+'/';
			file_pattern = dir_pattern + self.output['file_name_pattern'];
			
			basedir = self.insert_vars(dir_pattern, re);
			basefile = self.insert_vars(file_pattern, re);
			
			og = basefile;
			i=2;
			while next((s for s in self.used_filenames if basefile in s), None):
				print("\t!Incrementing duplicate filename.")
				basefile = og+' . '+str(i)+' ';
			
			data = {
				'parent_dir'	: basedir,			# Some handlers will need to build the parent directory for their single file first. This simplifies parsing.
				'single_file'	: basefile+"%s",	# If this handler can output a single file, it will use this path.
				'multi_dir' 	: basefile+"/",		# If the handler is going to download multiple files, it will save them under this directory.
				'post_title'	: re.title,			# The title of the Reddit post.
				'post_subreddit': re.subreddit,		# The subreddit this post came from.
			};
			
			re.add_file(url, False);# Default to 'False', meaning no file was located by a handler.
			for h in handlers:
				out("\tChecking handler: %s" % h.tag);
				ret = h.handle(url, data)
				if ret==None:
					# None is returned when the handler specifically wants this URL to be "finished", but not added to the files list.
					out("\t+Handler '%s' completed correctly, but returned no files!" % h.tag )
					re.add_file(url, None);
					break;
				if ret:
					out("\t+Handler '%s' completed correctly! %s" % (h.tag, StringUtil.fit(ret, 75)) )
					self.used_filenames.append(ret);
					# The handler will return a file/directory name if it worked properly.
					re.add_file(url, ret);
					break;
				#
			#
		#	
	#
	
	
#

auth = None;
settings = None;
if args.settings:
	settings = args.settings;
if args.test:
	print("Test Mode running")
if args.c_id and args.c_secret and args.password and args.agent and args.username:
	auth = {
        "client_id": args.c_id,
        "client_secret": args.c_secret,
        "password": args.password,
        "user_agent": args.agent,
        "username": args.username
    }
#
p = Scraper(settings_file = settings, override_login = auth);
p.run();

types_found = {};
if args.test:
	# Run some extremely basic tests to be sure (mostly) everything's working.
	# Uses data specific to a test user account. This functionality is useless outside of building.
	print("Checking premade data...");
	for e in p.elements:
		if e.author != 'theshadowmoose':
			print("Invalid author name from test data: "+str(e.author));
			sys.exit(100);
		if e.subreddit != 'shadow_test_sub':
			print('Invalid Subreddit: '+str(e.subreddit));
			sys.exit(101);
		if 'Test' not in e.title:
			print('Non-test title!: '+str(e.title));
			sys.exit(104);
		if e.type in types_found:
			types_found[e.type] = types_found[e.type]+1;
		else:
			types_found[e.type] = 1;
	#
	# Check that we found the correct # of posts/comments.
	if types_found['Comment'] != 1 or types_found['Post'] != 2:
		print('Invalid posts or comment parsing: '+str(types_found));
	# Check manifest was built (should always be during testing).
	if not os.path.exists(p.manifest_file):
		print('Failed to build manifest!');
		sys.exit(103);
	
	import glob
	import hashlib
	import fnmatch;
	# Make sure all test files downloaded properly:
	# This tests the Imgur downloader, as well as the file duplicate renaming, & the album naming.
	hashes = ['da0739019c490cbc4c184b9b2abca919','5d5a60b1eb50bc29d27f5f15ebea0e15','16392ddc40fabe7d8e9c467e7ab89fdf','e9cb466caa1e243e54d3e8d38bfd1162','9c100b8dc2dab4a33098bcb383468767']
	for root, dirnames, filenames in os.walk(p.download_dir):
		for filename in fnmatch.filter(filenames, '*.png'):
			digest = str(hashlib.md5( (str(open( os.path.join(root, filename) , 'rb').read())+filename).replace('/','.').replace('\\', '.').encode('utf-8') ).hexdigest());
			print('\t'+digest);
			if digest in hashes:
				hashes.remove( digest )
			else:
				print('Invalid file: '+str(filename));
				sys.exit(106);
				
	if len(hashes) > 0:
		print("Missing or incorrect file was downloaded!");
		sys.exit(105);
#