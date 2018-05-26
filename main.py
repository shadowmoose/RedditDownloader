#!/usr/bin/env python3

__version__ = "2.2"

import argparse
import sys
import os
import time
import datetime
import re

parser = argparse.ArgumentParser(description="Tool for scanning Reddit and downloading media - Guide @ https://goo.gl/hgBxN4")
parser.add_argument("--settings", help="Path to custom Settings file.", type=str, metavar='')
parser.add_argument("--test", help="Launch in Test Mode. Only used for TravisCI testing.",action="store_true")
parser.add_argument("--update", help="Update the program.", action="store_true")
parser.add_argument("--update_only", help="Update the program and exit.", action="store_true")
parser.add_argument("--skip_pauses", help="Skip all skippable pauses.", action="store_true")
parser.add_argument("--source", '-s', help="Run each loaded Source only if alias matches the given pattern. Can pass multiple patterns.", type=str, action='append', metavar='')
parser.add_argument("--category.setting", help="Override the given setting.", action="store_true")
parser.add_argument("--list_settings", help="Display a list of overridable settings.", action="store_true")
args, unknown_args = parser.parse_known_args()

if args.update or args.update_only: #!cover
	from classes.util.updater import Updater
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


import colorama
from colorama import Fore
from classes.util import settings
from classes.processing.elementprocessor import ElementProcessor
from classes.reddit.redditloader import RedditLoader
import classes.util.manifest as manifest
import classes.reddit.reddit as reddit
from classes.util import stringutil


colorama.init(convert=True)

stringutil.print_color(Fore.GREEN, """
====================================
    Reddit Media Downloader %s
====================================
    (By ShadowMoose @ Github)
""" % __version__)


class Scraper(object):
	def __init__(self,):
		if not os.path.isdir(settings.save_base()):
			os.makedirs(os.path.abspath(settings.save_base()) )
		os.chdir(settings.save_base()) # Hop into base dir, so all file work can be relative.

		manifest.create('manifest.sqldb')

		self.sources = self.load_sources()
		self.reddit = None
		self.processor = None
		
		# Authenticate and prepare to scan:
		reddit.init(client_id=settings.get('auth.client_id'), client_secret=settings.get('auth.client_secret'),
					password=settings.get('auth.password'), user_agent=settings.get('auth.user_agent'), username=settings.get('auth.username'))
		reddit.login()

		manifest.check_legacy(settings.save_base())  # Convert away from legacy Manifest.


	def run(self):
		_start_time = time.time()
		try:
			self.reddit = RedditLoader(args.test)
			self.reddit.scan(self.sources) # Starts the scanner thread.
			self.processor = ElementProcessor(self.reddit)
			self.processor.run()
		except KeyboardInterrupt:
			print("Interrupted by User.")
			if self.processor:
				self.processor.stop_process()
		_total_time = str( datetime.timedelta(seconds= round(time.time() - _start_time)) )
		print('Found %s posts missing files - with %s new files downloaded - and %s files that cannot be found.' %
			  (self.processor.total_posts, self.processor.total_urls, self.processor.failed_urls))
		print('Finished processing in %s.' % _total_time)


	def load_sources(self): #!cover
		sources = []
		settings_sources = settings.get_sources()
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


if args.list_settings:  #!cover
	print('All valid overridable settings:')
	for s in settings.get_all():
		if s.public:
			print("%s.%s" % (s.category, s.name))
			print('\tDescription: %s' % s.description)
			if not s.opts:
				print('\tValid value: \n\t\tAny %s' % s.type)
			else:
				print('\tValid values:')
				for o in s.opts:
					print('\t\t"%s": %s' % o)
			print()
	sys.exit()

settings_file = 'settings.json'
if args.settings:
	settings_file = args.settings #!cover
if args.test:
	print("Test Mode running")
	print('Using test settings file.')
	settings_file = './tests/test-settings.json'

_loaded = settings.load(settings_file)
if not _loaded:
	stringutil.error('Failed to load settings file!')
	print('A settings file has been created for you, at "%s". Please customize it.' % settings_file)
	# TODO: Prompt for WebUI instead.
	sys.exit(1)

for ua in unknown_args:
	k = ua.split('=')[0].strip('- ')
	v = ua.split('=', 2)[1].strip()
	try:
		settings.put(k, v, save_after=False)
	except KeyError:
		print('Unknown setting: %s' % k)
		sys.exit(50)


p = Scraper()
p.run()




if args.test:
	# Run some extremely basic tests to be sure (mostly) everything's working.
	# Uses data specific to a test user account. This functionality is useless outside of building.
	stringutil.print_color(Fore.YELLOW, "Checking against prearranged data...")
	
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
			if val != 0: #!cover
				stringutil.print_color(Fore.RED, 'FAIL: %s' % str(msg))
				exit_values.append(1000+i)  #use a unique error code for potential help debugging.
			else:
				stringutil.print_color(Fore.GREEN, 'PASSED')
		except Exception as e:
			stringutil.print_color(Fore.RED, 'EXCEPTION: %s' % e)
			exit_values.append(i)
			raise
	if max(exit_values) > 0: #!cover
		stringutil.print_color(Fore.RED, "Failed testing!")
		sys.exit( max(exit_values) )
	stringutil.print_color(Fore.GREEN, 'Passed all tests!')
	sys.exit(0)
#
