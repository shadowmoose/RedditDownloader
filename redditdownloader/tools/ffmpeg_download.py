import requests
from zipfile import ZipFile
from os.path import abspath, dirname, join
from processing.wrappers.rel_file import RelFile
import platform
import shutil
import os
import stat
import glob
from multiprocessing import Lock

"""
	THANKS TO https://ffbinaries.com/api/v1/version/latest, FOR PROVIDING THE BACKUP FFMPEG BINARIES RMD USES.
"""


_lock = Lock()
_versions = ['32', '64']
_os_opts = [('win', 'windows', 'ffmpeg.exe'), ('darwin', 'osx', 'ffmpeg'), ('linux', 'linux', 'ffmpeg')]

_os_version = '32'
_os_filename = None
for _v in _versions:
	if platform.machine().endswith(_v):
		_os_version = _v
		break

_current_os = None
for _o in _os_opts:
	if _o[0] in platform.system().lower():
		_current_os = _o[1]
		_os_filename = _o[2]


def _find_ffmpeg(abs_dir):
	match = glob.glob('%s*' % join(abs_dir, 'ffmpeg'))
	return match[0] if match else None


def _dl_binary(output_dir, verbose=True):
	output_dir = abspath(output_dir)
	output_zip = RelFile(base=output_dir, file_path='tmp-ffmpeg.zip')
	if _find_ffmpeg(output_dir):
		return _find_ffmpeg(output_dir)
	os.makedirs(output_dir, exist_ok=True)
	if verbose:
		print("Searching for FFmpeg binary...")
	dat = requests.get('https://ffbinaries.com/api/v1/version/latest').json()

	match = None
	possible = None
	for plat, files in dat['bin'].items():
		if _current_os in plat:
			if _os_version in plat:
				match = files
			else:
				possible = possible if possible else files
	matches = [m for m in [match, possible] if m]
	if not matches:
		raise Exception("Unable to locate possible FFmpeg archive match!")
	url = matches[0]['ffmpeg']
	if verbose:
		print("Downloading ffmpeg zip archive from: %s" % url)
	r = requests.get(url, stream=True)
	if r.status_code == 200:
		with open(output_zip.absolute(), 'wb') as f:
			r.raw.decode_content = True
			shutil.copyfileobj(r.raw, f)
	else:
		raise Exception("Unable to download FFmpeg archive!")

	with ZipFile(output_zip.absolute(), 'r') as z:
		extracted = z.extract(_os_filename, path=output_dir)
		if not extracted:
			raise Exception('Unable to extract FFmpeg binary!')
		st = os.stat(extracted)
		os.chmod(extracted, st.st_mode | stat.S_IEXEC)
	output_zip.delete_file()
	return extracted


def install_local(local_dir=None, verbose=True, force_download=False):
	""" Returns the absolute path to RMD's local ffmpeg binary, downloading the binary if required. None on error. """
	if not force_download:
		existing = shutil.which("ffmpeg")
		if existing:
			return abspath(existing)
	_lock.acquire()
	try:
		local_dir = local_dir if local_dir else join(abspath(dirname(dirname(dirname(__file__)))), 'bin')
		return _dl_binary(local_dir, verbose=verbose)
	except Exception as ex:
		print(ex)
		return None
	finally:
		_lock.release()


if __name__ == '__main__':
	print('FFmpeg location:', install_local())

