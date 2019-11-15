#!/usr/bin/env python3
"""
	This is a basic launcher, built to bootstrap RMD.
	This exists to simplify the installation process for users who are unfamiliar with python.

	This launcher will update all non-dev requirements, and then launch RMD.

	For the casual user this is the suggested way to launch RMD each time.
	It will update some often-changing dependencies (YTDL mostly), which lets RMD keep updated with online content changes.
"""

import os.path as path
import traceback
import sys
import importlib
import os

print('Python %s on %s' % (sys.version, sys.platform))
if sys.version_info < (3, 5):
	print('Error: RMD cannot run on a python version < 3.5. Please update your python installation, or run with "python3".')
	input("-Press [Enter] to quit-")
	sys.exit(1)

if path.isfile('/proc/version'):
	# Attempt to screen out WSL users, since it is currently (2019/10/21) known to be broken.
	try:
		with open('/proc/version', 'r') as o:
			txt = o.read()
			if 'microsoft' in txt.lower():
				print('Warning: Running RMD through a Windows-Linux subsystem is not supported, and will likely fail.')
				input("-Press [Enter] to continue anyways-")
	except Exception as e:
		print(e)
dr = path.abspath(path.dirname(path.abspath(__file__)))
sys.path.insert(0, path.join(dr, 'redditdownloader'))

issues = set()


def update_reqs():
	print("Updating requirements. This may take a while on first-time installs..")
	try:
		try:
			from pip import main as pipmain
		except ImportError:
			from pip._internal import main as pipmain
		pipmain(['install', '--upgrade', '-r', path.join(dr, 'requirements.txt')])
		print('\n'*10)
		os.system('cls' if os.name == 'nt' else 'clear')
	except Exception as ex:
		print(ex)


if __name__ == '__main__':
	if update_reqs():
		print('Requirements up to date!')
	# noinspection PyBroadException
	try:
		importlib.invalidate_caches()
		import redditdownloader.__main__ as rmd
		rmd.run()
	except Exception:
		traceback.print_exc()
		print('\n\nCaught a fatal error running RMD. Cannot continue.')
		input('-Press [Enter] to quit-')
