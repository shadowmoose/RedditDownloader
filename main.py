__version__ = "1.54"

import argparse
import sys
import os
parser = argparse.ArgumentParser(description="Tool for scanning Reddit and downloading media - Guide @ https://goo.gl/hgBxN4")
parser.add_argument('--wizard', '-w', help="Run the Setup Wizard to simplify editing settings.", action="store_true")
parser.add_argument("--settings", help="Path to custom Settings file.", type=str, metavar='')
parser.add_argument("--test", help="Launch in Test Mode. Only used for TravisCI testing.",action="store_true")
parser.add_argument("--update", help="Update the program.", action="store_true")
parser.add_argument("--update_only", help="Update the program and exit.", action="store_true")
parser.add_argument("--skip_pauses", help="Skip all skippable pauses.", action="store_true")
parser.add_argument('--duplicate','-nd', help='Skip deduplicating similar files.', action="store_true")
parser.add_argument('--skip_manifest', help='Skip using manifest to prevent rechecking existing downloads.', action="store_true")
parser.add_argument("--username", help="Reddit account username.", type=str, metavar='')
parser.add_argument("--password", help="Reddit account password.", type=str, metavar='')
parser.add_argument("--c_id", help="Reddit client id.", type=str, metavar='')
parser.add_argument("--c_secret", help="Reddit client secret.", type=str, metavar='')
parser.add_argument("--agent", help="String to use for User-Agent.", type=str, metavar='')

parser.add_argument("--base_dir", help="Override base directory.", type=str, metavar='')
parser.add_argument("--file_pattern", help="Override filename output pattern", type=str, metavar='')
parser.add_argument("--subdir_pattern", help="Override subdirectory name pattern", type=str, metavar='')
parser.add_argument("--source", '-s', help="Run each loaded Source only if alias matches the given pattern. Can pass multiple patterns.", type=str, action='append', metavar='')
args = parser.parse_args()

sys.path.insert(0, './classes')
sys.path.insert(0, './classes/handlers')
sys.path.insert(0, './classes/sources')
sys.path.insert(0, './classes/filters')
sys.path.insert(0, './classes/wizards')


if args.update or args.update_only:
	from updater import Updater
	upd = Updater('shadowmoose', 'RedditDownloader', __version__, args.skip_pauses) # Pull from the latest release
	upd.run()

	if args.update_only:
		print('Exit after update.')
		sys.exit(0)
	else:
		# The update process can actually update this main file, so we need to totally reload here.
		# This is handled in a simple exec() to avoid any crazy process starting.
		args = sys.argv[1:]
		for a in args:
			# Strip "update" commands before relaunching.
			if '--update' == a.lower():
				sys.argv.remove(a)
		with open(__file__) as source_file:
			exec(source_file.read())
			print("Exiting following update bootstrap.")
			sys.exit(0)

import time
import re
import colorama
from colorama import Fore

from settings import Settings
import stringutil
from elementprocessor import ElementProcessor
from redditloader import RedditLoader
from manifest import Manifest
import reddit
import wizards.wizard as wizard
import console

colorama.init(convert=True)

stringutil.print_color(Fore.GREEN, """
====================================
    Reddit Media Downloader %s
====================================
    (By ShadowMoose @ Github)
""" % __version__)


class Scraper(object):
	def __init__(self, settings_file, c_settings=None):
		self.settings = Settings(settings_file, can_save=(c_settings is None), can_load=(not args.test) )
		if c_settings:
			for k,v in c_settings.items():
				self.settings.set(k, v)
		#
		if args.wizard:
			if args.wizard and args.skip_pauses:
				stringutil.error('You cannot run the Wizard with pause skipping enabled.')
				sys.exit(16)
			print('\n\n')
			wizard.interact(self.settings)
			print('Exit after Wizard.')
			sys.exit(0)

		self.manifest = None
		if self.settings.get('build_manifest', True):
			self.manifest = Manifest(self.settings, True)
		else:
			print('Not using manifest.')

		self.sources = self.load_sources()
		self.reddit = None
		self.processor = None
		
		# Authenticate and prepare to scan:
		auth_info = self.settings.get('auth')
		if not auth_info:
			print('Error loading authentication information!')
			return
		self.settings.set('last_started', time.time())

		reddit.init(client_id=auth_info['client_id'], client_secret=auth_info['client_secret'],
					password=auth_info['password'], user_agent=auth_info['user_agent'], username=auth_info['username'])
		reddit.login()


	def run(self):
		try:
			self.reddit = RedditLoader()
			self.reddit.scan(self.sources)
			self.processor = ElementProcessor(self.reddit, self.settings, self.manifest)
			self.processor.run()
		except KeyboardInterrupt:
			print("Interrupted by User.")
		

		if self.manifest:
			if not args.skip_pauses:
				if console.confirm("Build manifest?", True):
					print('Building manifest.')
					self.manifest.build(self.reddit)
			else:
				print('Automatically building manifest.')
				self.manifest.build(self.reddit)
		else:
			print('Manifest not built.')
			if not args.skip_pauses:
				input("Press Enter to exit.")
		print('Download complete!')
	#


	def load_sources(self):
		sources = []
		settings_sources = self.settings.get_sources()
		if args.source is None:
			for s in settings_sources:
				print('Loaded Source: ', s.get_alias())
				sources.append(s)
		else:
			for so in args.source:
				regexp = re.compile(str(so), re.IGNORECASE)
				for s in settings_sources:
					if regexp.search( str(s.get_alias()) ):
						print('Matched Source: ', s.get_alias() )
						sources.append(s)
						break

		if len(sources) == 0:
			if len(settings_sources) == 0:
				stringutil.error('No sources were found from the settings file.')
			else:
				stringutil.error('No sources were found from the settings file matching the supplied patterns.')
			sys.exit(20)
		return sources


#


settings = 'settings.json'
if args.settings:
	settings = args.settings
if args.test:
	print("Test Mode running")
#

# Though the settings file can be manually edited, 
# Using the format default listed in 'settings', we allow the user to override most of them with command-line args.
# Simply pop key->value replacements into this obj to override those key->value pairs when the Scraper launches.
custom_settings = {}

if args.base_dir:
	mod = Settings(settings, False).get('output')# get default output format from a non-saving Settings object.
	mod['base_dir'] = args.base_dir
	if args.file_pattern:
		mod['file_name_pattern'] = args.file_pattern
	if args.subdir_pattern:
		mod['subdir_pattern'] = args.subdir_pattern
	custom_settings['output'] = mod

user_settings = [args.c_id , args.c_secret , args.password , args.agent , args.username]
if any(user_settings):
	if not all(user_settings):
		print('You must set all the Client, User, and User-Agent parameters to do that!')
		sys.exit(5)
	auth = {
		"client_id": args.c_id,
		"client_secret": args.c_secret,
		"password": args.password,
		"user_agent": args.agent,
		"username": args.username
	}
	print('Using command-line authorization details!')
	custom_settings['auth'] = auth

if args.duplicate:
	custom_settings['deduplicate_files'] = False

if args.skip_manifest:
	custom_settings['build_manifest'] = False


# If no settings were specified, pass 'None' to stick completely with default, auto-saving file values.
if len(custom_settings) == 0:
	print('Loading all settings from file.')
	custom_settings = None

p = Scraper(settings, custom_settings)
p.run()




if args.test:
	# Run some extremely basic tests to be sure (mostly) everything's working.
	# Uses data specific to a test user account. This functionality is useless outside of building.
	stringutil.print_color(Fore.YELLOW, "Checking against prearranged data...")
	if not os.path.isdir('tests'):
		stringutil.print_color(Fore.RED, 'No tests directory found.')
		sys.exit(1)
	
	# Import all the testing modules.
	import os.path
	import pkgutil
	import tests
	pkg_path = os.path.dirname(tests.__file__)
	padding_len = str(max([len(name) for _, name, _ in pkgutil.iter_modules([pkg_path])]))
	i = 0
	exit_values = [0]
	for _,name,_ in pkgutil.iter_modules([pkg_path]):
		i+=1
		try:
			print( ("\t%3d:%-"+padding_len+"s -> ") % (i, name) , end='')
			name = "tests." + name
			test = __import__(name, fromlist=[''])
			msg,val = test.run_test(p.reddit)
			if val != 0:
				stringutil.print_color(Fore.RED, 'FAIL: %s' % str(msg))
				exit_values.append(1000+i)  #use a unique error code for potential help debugging.
			else:
				stringutil.print_color(Fore.GREEN, 'PASSED')
		except Exception as e:
			stringutil.print_color(Fore.RED, 'EXCEPTION: %s' % e)
			exit_values.append(i)
	if max(exit_values) > 0:
		stringutil.print_color(Fore.RED, "Failed testing!")
		sys.exit( max(exit_values) )
	stringutil.print_color(Fore.GREEN, 'Passed all tests!')
	sys.exit(0)
#
