import eel
import sys
import os
import base64
from classes.static import settings
from classes.sources import source
from classes.filters import filter
from classes.static import manifest
from classes.downloader import RMD

_file_dir = None
_web_dir = None
_rmd_version = '0'
_downloader = None
_downloader_args = {}

"""
	Eel is great, but doesn't expose everything we want.
	So by locking Eel to specific versions, we can easily override whatever we need here.
	
	See simple documentation: https://bottlepy.org/docs/dev/tutorial.html
"""


def start(web_dir, file_dir, rmd_version, downloader_args, relaunched=False):
	global _file_dir, _web_dir, _rmd_version, _downloader_args
	_file_dir = os.path.abspath(file_dir)
	_web_dir = os.path.abspath(web_dir)
	_rmd_version = rmd_version
	_downloader_args = downloader_args
	if not settings.get('interface.start_server'):
		print('WebUI is disabled by settings.')
		return False
	browser = settings.get('interface.browser').lower().strip()
	browser = None if (browser == 'off' or relaunched) else browser
	options = {
		'mode': browser,
		'host': settings.get('interface.host'),
		'port': settings.get('interface.port'),
		'chromeFlags': []
	}

	eel.init(web_dir)
	eel.start('index.html', options=options, block=False, callback=_websocket_close)
	# interface.port
	print('Started WebUI!')
	if browser:
		print('Awaiting connection from browser...')
	else:
		print('Browser auto-opening is disabled! Please open a browser to http://%s:%s/index.html !' %
			  (options['host'], options['port']))
	return True


def _websocket_close(page, websockets):
	print('A WebUI just closed. (%s)' % page)
	eel.sleep(2.0)
	if len(websockets) == 0 and not settings.get('interface.keep_open'):
		print('WebUI keep_open is disabled, and all open clients have closed.\nExiting.')
		sys.exit()


@eel.btl.route('/file')
def _downloaded_files():
	""" Allows the UI to request files RMD has scraped.
		In format: "./file?id=file_token"
	"""
	token = eel.btl.request.query.id
	file_path = base64.decodebytes(token.replace(' ', '+').encode()).decode()
	print('Requested RMD File: %s' % file_path)
	return eel.btl.static_file(file_path, root=_file_dir)


# ======  JS->Python API functions:  ======
@eel.expose
def api_current_status():
	return {'current_version': _rmd_version}


@eel.expose
def api_get_settings():
	return settings.to_obj(save_format=False, include_private=False)


@eel.expose
def api_save_settings(settings_obj):
	print('WebUI wants to change settings:', settings_obj)
	# noinspection PyBroadException
	try:
		for k, v in settings_obj.items():
			settings.put(k, v, save_after=False)
		settings.save()
	except Exception:
		import traceback
		traceback.print_exc()
		return False
	return True


@eel.expose
def api_get_sources():
	ret = {'available': [], 'active': [], 'filters': {}}
	for s in source.get_sources():
		ret['available'].append(s.to_obj(for_webui=True))
	for s in settings.get_sources():
		ret['active'].append(s.to_obj(for_webui=True))
	ret['filters']['available'] = [f.to_js_obj() for f in filter.get_filters()]
	ret['filters']['operators'] = [f.value for f in filter.Operators]
	return ret


@eel.expose
def api_save_sources(new_obj):
	print('Saving new source list:')
	output_settings = []
	for so in new_obj:
		print('\tType:', so['type'], 'Alias:', so['alias'])
		all_sources = source.get_sources()
		for s in all_sources:
			if s.type == so['type']:
				s.set_alias(so['alias'])
				for k, v in so['data'].items():
					s.insert_data(k, v)
				for f in so['filters']:
					for fi in filter.get_filters():
						if f['field'] == fi.field:
							fi.set_operator(f['operator'])
							fi.set_limit(f['limit'])
							s.add_filter(fi)
							break
				output_settings.append(s)
	for s in settings.get_sources():
		settings.remove_source(s, save_after=False)
	for s in output_settings:
		settings.add_source(s, prevent_duplicate=False, save_after=False)
	return settings.save()


@eel.expose
def api_searchable_fields():
	return list(set(manifest.get_searchable_fields()))


@eel.expose
def api_search_posts(fields, term):
	obj = {}

	def b64(str_in):
		return base64.encodebytes(str_in.encode()).decode()

	def explode(file):
		if os.path.isfile(file):
			return [{'token': b64(file), 'path': file}]
		elif os.path.isdir(file):
			return [{'token': b64(os.path.join(file, _f)), 'path': os.path.join(file, _f)} for _f in os.listdir(file) if os.path.isfile(os.path.join(file, _f))]
		else:
			return None

	for p in manifest.search_posts(fields, term):
		if p['id'] not in obj:
			p['files'] = explode(p['file_path'])
			del p['file_path']
			obj[p['id']] = p
		else:
			for f in explode(p['file_path']):
				obj[p['id']]['files'].append(f)
	# import json
	# print('Sending file list:', json.dumps(list(obj.values()), indent=4, sort_keys=True, separators=(',', ': ')))
	return list(obj.values())


@eel.expose
def api_search_nested_posts(fields, term):
	obj = {}
	for p in manifest.search_posts(fields, term):
		if p['type'] == 'Submission':
			p['children'] = []
			obj[p['id']] = p
		else:
			if p['parent'] in obj:
				obj[p['parent']]['children'].append(p)
			else:
				obj[p['id']] = p
	return list(obj.values())


@eel.expose
def restart():
	""" API to terminate with special "restart" code, which the Bootstrap uses as a signal to relaunch. """
	sys.exit(202)

@eel.expose
def start_download():
	global _downloader
	if _downloader is not None and _downloader.is_running():
		return {'error': 'Error starting downloader - already running!'}
	else:
		_downloader = RMD(**_downloader_args)
		_downloader.start()
		return {'status': 'Started downloader!'}


@eel.expose
def download_status():
	if _downloader is None:
		return {'running': False}
	return {
		'running': _downloader.is_running()
		# TODO: More information here: progress report, etc.
	}


def sleep(sec):
	eel.sleep(sec)


if __name__ == '__main__':
	settings.load('test-webui-settings.json')
	opened = start('../../web/', '../../../download', '1.5', {})
	while opened:
		sleep(60)
