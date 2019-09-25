import urllib.request
import json
import sys
import traceback

pypy_name = 'RedditDownloader'
current_version = "3.0.0"
author = "ShadowMoose"


_latest_version = None


def latest_version():
	global _latest_version
	if _latest_version is None:
		# noinspection PyBroadException
		try:
			with urllib.request.urlopen("https://pypi.org/pypi/%s/json" % pypy_name) as fp:
				resp = json.load(fp)
				_latest_version = resp['info']['version']
		except Exception:
			traceback.print_exc()
			print('Error searching for latest version! Please check manually.', file=sys.stderr)
			_latest_version = False
	return _latest_version or None


def get_available_update():
	if len(current_version.split('-')) > 1:
		print('Cannot check for new %s versions from special releases.' % pypy_name)
		return False
	lv = latest_version()
	if lv and lv != current_version:
		return lv
	return False


if __name__ == '__main__':
	print('Latest %s version:' % pypy_name, latest_version())
	print('Update Available:', get_available_update())
