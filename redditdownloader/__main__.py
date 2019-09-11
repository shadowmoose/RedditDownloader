#!/usr/bin/env python3

__version__ = "3.0.0"

import argparse
import sys
import static.stringutil as su
import static.settings as settings
import static.console as console
from sources import DirectInputSource
from interfaces.terminal import TerminalUI
from interfaces.eelwrapper import WebUI
import tests.runner
import sql
from tools import ffmpeg_download
import re


parser = argparse.ArgumentParser(
	description="Tool for scanning Reddit and downloading media - Guide @ https://goo.gl/hgBxN4")
parser.add_argument("--settings", help="Path to custom Settings file.", type=str, metavar='', default="./settings.json")
parser.add_argument("--source", '-s',
					help="Run each configured Source only if its alias matches the given pattern. Can pass multiple patterns.",
					type=str, action='append', metavar='')
parser.add_argument("--category.setting", help="Override the given setting(s).", action="store_true")
parser.add_argument("--list_settings", help="Display a list of overridable settings.", action="store_true")
parser.add_argument("--version", '-v', help="Print the current version and exit.", action="store_true")
parser.add_argument("--run_tests", help="Run the given test directory, or * for all.", type=str, metavar='', default="")
parser.add_argument("--limit", help="For direct downloading of user/subreddit, set the limit here.", type=int, default=1000)
args, unknown_args = parser.parse_known_args()


direct_sources = []


if __name__ == '__main__':
	su.print_color('green', "\r\n" +
		'====================================\r\n' +
		('   Reddit Media Downloader %s\r\n' % __version__) +
		'====================================\r\n' +
		'    (By ShadowMoose @ Github)\r\n')
	if args.version:
		sys.exit(0)

	if args.run_tests:
		error_count = tests.runner.run_tests(test_subdir=args.run_tests)
		sys.exit(error_count)

	if args.list_settings:
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
			if 'r/' or 'u/' in ua:
				direct_sources.append(DirectInputSource(txt=ua, args={'limit': args.limit}))
				continue
			else:
				su.error("ERROR: Unkown argument: %s" % ua)
				sys.exit(1)
		k = ua.split('=')[0].strip('- ')
		v = ua.split('=', 2)[1].strip()
		try:
			settings.put(k, v, save_after=False)
		except KeyError:
			print('Unknown setting: %s' % k)
			sys.exit(50)

	if args.source:
		matched_sources = set()
		for s in args.source:
			for stt in settings.get_sources():
				if re.match(s, stt.get_alias()):
					matched_sources.add(stt)
		direct_sources.extend(matched_sources)

	if not ffmpeg_download.install_local():
		print("RMD was unable to locate (or download) a working FFmpeg binary.")
		print("For downloading and post-processing, this is a required tool.")
		print("Please Install FFmpeg manually, or download it from here: https://rmd.page.link/ffmpeg")
		sys.exit(15)

	if not _loaded and not direct_sources:
		# First-time configuration.
		su.error('Could not find an existing settings file. A new one will be generated!')
		if not console.confirm('Would you like to start the WebUI to help set things up?', True):
			su.print_color('red', "If you don't open the webUI now, you'll need to edit the settings file yourself.")
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

	# Initialize Database
	sql.init_from_settings()

	if direct_sources:
		settings.disable_saving()
		for s in settings.get_sources():
			settings.remove_source(s, save_after=False)
		for d in direct_sources:
			settings.add_source(d, prevent_duplicate=False, save_after=False)

	ui = None
	if settings.get('interface.start_server') and not direct_sources:
		print("Starting WebUI...")
		ui = WebUI(__version__)
	else:
		ui = TerminalUI(__version__)
	ui.display()
