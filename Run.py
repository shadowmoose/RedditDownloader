#!/usr/bin/env python3
"""
	This is a basic launcher, built to bootstrap RMD.
	This exists to simplify the installation process for users who are unfamiliar with python.

	If run from a binary, this launcher will auto-update from the GitHub repo, and then launch RMD.

	For the casual user this is the suggested way to launch RMD each time.
	It will update some often-changing dependencies (YTDL mostly), which lets RMD keep updated with online content changes.
"""

import subprocess
import urllib.request
import os
from os.path import exists, join, abspath, dirname, basename, splitext
import sys
import json
import platform
import hashlib
import traceback
import multiprocessing

dr = abspath(dirname(abspath(__file__)))
sys.path.insert(0, join(dr, 'redditdownloader'))

OWNER = 'shadowmoose'
REPO = 'RedditDownloader'
DATA_BRANCH = 'release-metadata-3.x'


UPDATE_URL = 'https://raw.githubusercontent.com/%s/%s/%s/release.json' % (OWNER, REPO, DATA_BRANCH)
PROJECT_URL = 'https://github.com/%s/%s' % (OWNER, REPO)

frozen = getattr(sys, 'frozen', False)
application_path = os.path.abspath(__file__)
if frozen:
	application_path = os.path.abspath(sys.executable)
fname = basename(application_path)
base_dir = dirname(application_path)
backup_path = join(base_dir, 'backup-'+fname)
check_update = not any('--skip_update' in a for a in sys.argv)


def resource_path(relative_path):
	""" Get the absolute path to resources, even if frozen. """
	base_path = getattr(sys, '_MEIPASS', dr)
	return abspath(join(base_path, relative_path))


def get_os():
	p = platform.system().lower()
	if 'darwin' in p:
		return 'macOS'
	if 'linux' in p:
		return 'ubuntu'
	if 'win' in p:
		return 'windows'


def read_json(url):
	response = urllib.request.urlopen(url)
	return json.loads(response.read().decode('utf-8'))


def get_app_hash(file_path=None):
	hasher = hashlib.sha256()
	with open(file_path or application_path, 'rb') as _f:
		buf = _f.read(65536)
		while len(buf) > 0:
			hasher.update(buf)
			buf = _f.read(65536)
	return hasher.hexdigest()


def download(url, location, validate_hash=None):
	print('Downloading update from URL:', url)
	if exists(backup_path):
		print('Cleaning up old backup...')
		os.unlink(backup_path)
	if exists(location):
		print('Moving existing executable to backup...')
		os.renames(location, backup_path)

	try:
		urllib.request.urlretrieve(url, location)
		if validate_hash != get_app_hash(location):
			raise Exception('The downloaded file is malformed, or does not match hashes! %s' % get_app_hash(location))
		else:
			make_executable(location)
	except Exception as e:
		print('Error downloading update!', e)
		if exists(location):  # Roll back if download fails.
			os.unlink(location)
		os.renames(backup_path, location)
		return False
	print('Done downloading!')
	return True


def check_standalone_update():
	system = get_os()
	print('Checking for a standalone release update for platform %s...' % system)
	if not system:
		print('Error: Unable to determine which OS you are running!', platform.system())
		raise EnvironmentError('Unsupported platform system!')

	if exists(backup_path):
		try:
			print("Cleaning up old backup file...")
			os.unlink(backup_path)
		except Exception as e:
			print(e)

	metadata = read_json(UPDATE_URL)
	asset = next((a for a in metadata['assets'] if splitext(basename(a['name']))[0].lower().endswith(system.lower())), None)
	if not asset:
		raise EnvironmentError('Unable to locate a matching binary to update with!')

	asset_hash = asset['metadata']['sha256']
	if asset_hash != get_app_hash():
		print('Hash mismatch! Time to update...', get_app_hash())
		downloaded = download(asset['browser_download_url'], application_path, asset_hash)
		if not downloaded:
			raise RuntimeError('Unable to download update! Check %s for details!' % UPDATE_URL)
		else:
			return True
	return False


def launch_detatched():
	proc = sys.argv + ['--skip_update']
	cls()
	print('Launching:', proc)
	return subprocess.call(proc)


def cls():
	# noinspection PyBroadException
	try:
		print('\n'*10)
		os.system('cls' if os.name == 'nt' else 'clear')
	except Exception:
		pass


def make_executable(path):
	mode = os.stat(path).st_mode
	mode |= (mode & 0o444) >> 2    # copy R bits to X
	os.chmod(path, mode)


if __name__ == '__main__':
	multiprocessing.freeze_support()
	print('Python %s on %s' % (sys.version, sys.platform))
	if sys.version_info < (3, 5):
		print('Error: RMD cannot run on a python version < 3.5. Please update your python installation, or run with "python3".')
		input("-Press [Enter] to quit-")
		sys.exit(1)

	if check_update:
		try:
			if frozen:
				updated = check_standalone_update()
				if updated:
					print('Update downloaded. Relaunching...')
					launch_detatched()
					sys.exit(0)
		except Exception as ex:
			print(ex)
			traceback.print_exc()
			print('\n\nUnable to download upate! Please manually check the project: %s' % PROJECT_URL, file=sys.stderr)

	# noinspection PyBroadException
	try:
		# Launch the main RMD python app.
		import redditdownloader.__main__
		redditdownloader.__main__.run()
	except KeyboardInterrupt:
		pass
	except Exception:
		traceback.print_exc()
		print('\n\nCaught a fatal error running RMD. Cannot continue.')
		input('-Press [Enter] to quit-')
