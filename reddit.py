import argparse
import sys;
parser = argparse.ArgumentParser(description="Save all Media Upvoted & Saved on Reddit")
parser.add_argument("--settings", help="path to custom Settings file.", type=str, metavar='')
parser.add_argument("--test", help="launch in Test Mode. Only used for TravisCI testing.",action="store_true")
parser.add_argument("--update", help="Update modules.", action="store_true")
parser.add_argument("--update_only", help="Only update modules and exit.", action="store_true")
parser.add_argument("--skip_pauses", help="Skip all skippable pauses", action="store_true")
parser.add_argument("--username", help="account username.", type=str, metavar='')
parser.add_argument("--password", help="account password.", type=str, metavar='')
parser.add_argument("--c_id", help="Reddit client id.", type=str, metavar='')
parser.add_argument("--c_secret", help="Reddit client secret.", type=str, metavar='')
parser.add_argument("--agent", help="String to use for User-Agent.", type=str, metavar='')

parser.add_argument("--base_dir", help="override base directory.", type=str, metavar='')
parser.add_argument("--file_pattern", help="override filename output pattern", type=str, metavar='')
parser.add_argument("--subdir_pattern", help="override subdirectory name pattern", type=str, metavar='')
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
from updater import Updater;

print("""
=============================
   Reddit Media Downloader
=============================
""");

if args.update or args.update_only:
	# Attempt to update the handlers.
	print('Launching updater...');
	print('Make sure to visit https://travis-ci.org/shadowmoose/RedditDownloader and make sure that the latest build is passing!');
	if not args.skip_pauses:
		if 'c' in input('Press enter to continue (enter "c" to abort): ').lower():
			print('Aborted update');
			sys.exit(1);
	Updater('handlers', 'https://api.github.com/repos/shadowmoose/RedditDownloader/contents/handlers?ref=master', args.skip_pauses).run();
	if args.update_only:
		print('Exit after update.');
		sys.exit(0);

handlers = [];
for module in os.listdir('handlers'):
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
	
	def __init__(self, settings_file, custom_settings=None):
		self.settings = Settings(settings_file, custom_settings==None );
		if custom_settings:
			for k,v in custom_settings.items():
				self.settings.set(k, v);
		self.reddit = None;
		self.me = None;
		self.output = self.settings.get('output');
		self.download_dir = self.output['base_dir'];
		self.manifest_file = self.download_dir+'/manifest.json';
		
		self.all_reddit = [];# List of all posts we've liked/saved. Stored initially to avoid timeouts.
		self.elements = [];# List of Reddit Element wrappers
		self.used_filenames = [];# Keep a local list of used filenames, just for ease of lookup.
		
		
		
		# Authenticate and prepare to scan:
		info = self.settings.get('auth');
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

settings = 'settings.json';
if args.settings:
	settings = args.settings;
if args.test:
	print("Test Mode running")
#

# Though the settings file can be manually edited, 
# Using the format default listed in 'settings', we allow the user to override most of them with command-line args.
# Simply pop key->value replacements into this obj to override those key->value pairs when the Scraper launches.
custom_settings = {};

if args.base_dir:
	mod = Settings(settings, False).get('output');# get default output format from a non-saving Settings object.
	mod['base_dir'] = args.base_dir;
	if args.file_pattern:
		mod['file_name_pattern'] = arg.file_pattern;
	if args.subdir_pattern:
		mod['subdir_pattern'] = args.subdir_pattern;
	custom_settings['output'] = mod;

user_settings = [args.c_id , args.c_secret , args.password , args.agent , args.username]
if any(user_settings):
	if not all(user_settings):
		print('You must set all the Client, User, and User-Agent parameters to do that!');
		sys.exit(5);
	auth = {
		"client_id": args.c_id,
		"client_secret": args.c_secret,
		"password": args.password,
		"user_agent": args.agent,
		"username": args.username
	}
	print('Using command-line authorization details!');
	custom_settings['auth'] = auth;

# If no settings were specified, pass 'None' to stick completely with default, auto-saving file values.
if len(custom_settings) == 0:
	print('Using file values.');
	custom_settings = None;

p = Scraper(settings, custom_settings);
p.run();

if args.test:
	# Run some extremely basic tests to be sure (mostly) everything's working.
	# Uses data specific to a test user account. This functionality is useless outside of building.
	print("Checking against prearranged data...");
	if not os.path.isdir('tests'):
		print('No tests directory found.');
		sys.exit(1);
	
	# Import all the testing modules.
	import os.path, pkgutil
	import tests
	pkgpath = os.path.dirname(tests.__file__);
	padding_len = str(max( [len(name) for _, name, _ in pkgutil.iter_modules([pkgpath])]) );
	i = 0;
	exit_values = [0];
	for _,name,_ in pkgutil.iter_modules([pkgpath]):
		i+=1;
		try:
			print(("\t%3d:%-"+padding_len+"s -> ") % (i, name), end='');
			name = "tests." + name
			test = __import__(name, fromlist=[''])
			msg,val = test.run_test(p);
			if val != 0:
				print( 'FAIL: %s' % str(msg) );
				exit_values.append(1000+i);# use a unique error code for potential help debugging.
			else:
				print('PASSED');
		except Exception as e:
			print('EXCEPTION:', e);
			exit_values.append(i);
	if max(exit_values) > 0:
		sys.exit( max(exit_values) );
	print('Passed all tests!');
	sys.exit(0);
#