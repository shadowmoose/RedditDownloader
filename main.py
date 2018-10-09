#!/usr/bin/env python3

__version__ = "2.3"

import argparse
import sys
import os
import time
import subprocess

SCRIPT_BASE = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))

parser = argparse.ArgumentParser(
	description="Tool for scanning Reddit and downloading media - Guide @ https://goo.gl/hgBxN4")
parser.add_argument("--settings", help="Path to custom Settings file.", type=str, metavar='')
parser.add_argument("--test", help="Launch in Test Mode. Only used for TravisCI testing.", action="store_true")
parser.add_argument("--update", help="Update the program.", action="store_true")
parser.add_argument("--update_only", help="Update the program and exit.", action="store_true")
parser.add_argument("--skip_pauses", help="Skip all skippable pauses.", action="store_true")
parser.add_argument("--source", '-s',
					help="Run each loaded Source only if alias matches the given pattern. Can pass multiple patterns.",
					type=str, action='append', metavar='')
parser.add_argument("--category.setting", help="Override the given setting.", action="store_true")
parser.add_argument("--list_settings", help="Display a list of overridable settings.", action="store_true")
parser.add_argument("--version", '-v', help="Print the current version and exit.", action="store_true")
parser.add_argument("--wizard", '-w', help="Legacy, no longer does anything.", action="store_true")
parser.add_argument("--no_restart", help="If RMD should not be capable of restarting itself.", action="store_true")
parser.add_argument("--relaunched", help="Internal use. If RMD has bootstrapped at least once.", action="store_true")
args, unknown_args = parser.parse_known_args()

if args.update or args.update_only:  # !cover
	from classes.static.updater import Updater
	upd = Updater('shadowmoose', 'RedditDownloader', __version__, args.skip_pauses)  # Pull from the latest release
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

if args.wizard:
	print('The Wizard has been replaced by the built-in WebUI.')
	sys.exit(1)

from classes.webserver import eelwrapper
import colorama
from colorama import Fore
from classes.static import settings
from classes.static import stringutil
from classes.static import console
from classes.static import manifest
from classes.downloader import RMD

colorama.init(convert=True)
stringutil.print_color(Fore.GREEN, """
====================================
    Reddit Media Downloader %s
====================================
    (By ShadowMoose @ Github)
""" % __version__)

if args.version:
	sys.exit(0)

if args.list_settings:  # !cover
	print('All valid overridable settings:')
	for _s in settings.get_all():
		if _s.public:
			print("%s.%s" % (_s.category, _s.name))
			print('\tDescription: %s' % _s.description)
			if not _s.opts:
				print('\tValid value: \n\t\tAny %s' % _s.type)
			else:
				print('\tValid values:')
				for o in _s.opts:
					print('\t\t"%s": %s' % o)
			print()
	sys.exit()

settings_file = 'settings.json'
if args.settings:
	settings_file = args.settings  # !cover
if args.test:
	print("Test Mode running")
	print('Using test settings file.')
	settings_file = './tests/test-settings.json'

_loaded = settings.load(settings_file)

for ua in unknown_args:
	k = ua.split('=')[0].strip('- ')
	v = ua.split('=', 2)[1].strip()
	try:
		settings.put(k, v, save_after=False)
	except KeyError:
		print('Unknown setting: %s' % k)
		sys.exit(50)

if not _loaded:
	# First-time configuration.
	stringutil.error('Failed to load settings file! A new one will be generated!')
	if not args.skip_pauses:
		if not console.confirm('Would you like to start the WebUI to help set things up?', True):
			stringutil.print_color(Fore.RED,
								   "If you don't open the webUI now, you'll need to edit the settings file yourself.")
			if console.confirm("Are you sure you'd like to edit settings without the UI (if 'yes', these prompts will not show again)?"):
				settings.put('interface.start_server', False)  # Creates a save.
				print('A settings file has been created for you, at "%s". Please customize it.' % settings_file)
			else:
				print('Please re-run RMD to configure again.')
			sys.exit(1)
		else:
			mode = console.prompt_list('How would you like to open the UI?',
									   settings.get('interface.browser', full_obj=True).opts)
			settings.put('interface.browser', mode, save_after=False)
			settings.put('interface.start_server', True)
	else:
		print('Skipping prompts is enabled, please edit the settings file yourself.')
		settings.put('interface.start_server', False)
		sys.exit(1)

if settings.get('interface.start_server') and not args.no_restart and not args.test:
	# If run in UI mode, the initial script will stick here & reboot copies as needed.
	# A new RMD instance is only started if the last one exited with the special "restart" code.
	# This should always be performed before any DB or PRAW initialization, because it needs neither.
	relaunching = False
	while True:
		print('BOOTSTRAPPING RMD...')
		sargs = list(filter(lambda x: not x.startswith('--update'), sys.argv[:]))  # get running script args
		sargs.insert(len(sargs), '--no_restart')  # tell the child process to not enter this loop.
		sargs.insert(0, sys.executable)  # give it the executable
		if relaunching:
			sargs.insert(len(sargs), '--relaunched')  # tell the child process it has already run once.
		print('Launching: ', (sys.executable, sargs))
		ret = subprocess.call(sargs)
		if ret != 202:
			sys.exit(ret)
		print('Relaunching in 30 seconds... (CWD: %s)' % os.getcwd())
		relaunching = True
		# Wait for UI sockets to recycle - Maybe 60s (or a check if possible cross-platform)?

# Initialize all database and reddit connections.
if not os.path.isdir(settings.save_base()):
	os.makedirs(os.path.abspath(settings.save_base()))
os.chdir(settings.save_base())  # Hop into base dir, so all file work can be relative.

manifest.create('manifest.sqldb')
manifest.check_legacy(settings.save_base())  # Convert away from legacy Manifest.


test_downloader = None

# Only starts if the settings allow it to.
if not args.test \
		and settings.get('interface.start_server') \
		and eelwrapper.start(os.path.join(SCRIPT_BASE, 'web'), './',  __version__, args.relaunched):
	print('WebUI is now in control.')
	try:
		while True:
			eelwrapper.sleep(600)  # Eel will terminate with a sys.exit() call, when it's time to exit.
	except KeyboardInterrupt:
		print('\nUser terminated WebUI loop.')
else:
	p = RMD(source_patterns=args.source, test=args.test)
	test_downloader = p
	try:
		p.start()
		while p.is_running():
			time.sleep(0.25)
	except KeyboardInterrupt:
		stringutil.error('\nProcess interrupted by user! Shutting down...')
		p.stop()

if args.test:
	# Run some extremely basic tests to be sure (mostly) everything's working.
	# Uses data specific to a test user account. This functionality is useless outside of building.
	stringutil.print_color(Fore.YELLOW, "Checking against prearranged data...")

	# Import all the testing modules.
	import pkgutil
	import tests

	pkg_path = os.path.dirname(tests.__file__)
	padding_len = str(max([len(name) for _, name, _ in pkgutil.iter_modules([pkg_path])]))
	i = 0
	exit_values = [0]
	for _, name, _ in pkgutil.iter_modules([pkg_path]):
		i += 1
		try:
			print(("\t%3d:%-" + padding_len + "s -> ") % (i, name), end='')
			name = "tests." + name
			test = __import__(name, fromlist=[''])
			msg, val = test.run_test(test_downloader.loader)
			if val != 0:  # !cover
				stringutil.print_color(Fore.RED, 'FAIL: %s' % str(msg))
				exit_values.append(1000 + i)  # use a unique error code for potential help debugging.
			else:
				stringutil.print_color(Fore.GREEN, 'PASSED')
		except Exception as e:
			stringutil.print_color(Fore.RED, 'EXCEPTION: %s' % e)
			exit_values.append(i)
			raise
	if max(exit_values) > 0:  # !cover
		stringutil.print_color(Fore.RED, "Failed testing!")
		sys.exit(max(exit_values))
	stringutil.print_color(Fore.GREEN, 'Passed all tests!')
	sys.exit(0)
