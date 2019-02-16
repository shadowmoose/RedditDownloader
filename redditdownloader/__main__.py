#!/usr/bin/env python3

__version__ = "3.0"

import argparse
import sys
import colorama
from colorama import Fore
import static.stringutil as su
import static.settings as settings
import static.console as console

parser = argparse.ArgumentParser(
	description="Tool for scanning Reddit and downloading media - Guide @ https://goo.gl/hgBxN4")
parser.add_argument("--settings", help="Path to custom Settings file.", type=str, metavar='', default="./settings.json")
parser.add_argument("--source", '-s',
					help="Run each loaded Source only if alias matches the given pattern. Can pass multiple patterns.",
					type=str, action='append', metavar='')
parser.add_argument("--category.setting", help="Override the given setting.", action="store_true")
parser.add_argument("--list_settings", help="Display a list of overridable settings.", action="store_true")
parser.add_argument("--version", '-v', help="Print the current version and exit.", action="store_true")
args, unknown_args = parser.parse_known_args()


if args.version:
	print("RMD Version: %s" % __version__)
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

_loaded = settings.load(args.settings)
for ua in unknown_args:
	if '=' not in ua:
		su.error("ERROR: Unkown argument: %s" % ua)
		sys.exit(1)
	k = ua.split('=')[0].strip('- ')
	v = ua.split('=', 2)[1].strip()
	try:
		settings.put(k, v, save_after=False)
	except KeyError:
		print('Unknown setting: %s' % k)
		sys.exit(50)

if not _loaded:
	# First-time configuration.
	su.error('Failed to load settings file! A new one will be generated!')
	if not console.confirm('Would you like to start the WebUI to help set things up?', True):
		su.print_color(Fore.RED, "If you don't open the webUI now, you'll need to edit the settings file yourself.")
		if console.confirm("Are you sure you'd like to edit settings without the UI (if 'yes', these prompts will not show again)?"):
			settings.put('interface.start_server', False)  # Creates a save.
			print('A settings file has been created for you, at "%s". Please customize it.' % args.settings)
		else:
			print('Please re-run RMD to configure again.')
		sys.exit(1)
	else:
		mode = console.prompt_list('How would you like to open the UI?',
								   settings.get('interface.browser', full_obj=True).opts)
		settings.put('interface.browser', mode, save_after=False)
		settings.put('interface.start_server', True)

print("Loaded settings:", settings.get("auth.refresh_token"))

if __name__ == '__main__':
	colorama.init(convert=True)
	su.print_color(Fore.GREEN, """
	====================================
		Reddit Media Downloader %s
	====================================
		(By ShadowMoose @ Github)
	""" % __version__)

	# TODO: Create the Database if one doesn't exist.

	if settings.get('interface.start_server'):
		print("Starting WebUI...")
		sys.exit(0)  # TODO: Start Eel server.
	else:
		import downloader as downloader
		rmd = downloader.RMD()
		rmd.start()
