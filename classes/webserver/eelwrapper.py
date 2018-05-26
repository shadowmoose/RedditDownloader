import eel
import sys
import os
from classes.util import settings
from classes.sources import source
from classes.filters import filter


_file_dir = None
_web_dir = None

"""
	Eel is great, but doesn't expose everything we want.
	So by locking Eel to specific versions, we can easily override whatever we need here.
	
	See simple documentation: https://bottlepy.org/docs/dev/tutorial.html
"""

def start(web_dir, file_dir):
	global _file_dir, _web_dir
	_file_dir = os.path.abspath(file_dir)
	_web_dir = os.path.abspath(web_dir)
	if not settings.get('interface.start_server'):
		print('WebUI is disabled by settings.')
		return False
	browser = settings.get('interface.browser').lower().strip()
	browser = None if browser == 'off' else browser
	options = {
		'mode': browser,
		'host': settings.get('interface.host'),
		'port': settings.get('interface.port'),
		'chromeFlags': []
	}

	eel.init(web_dir)
	eel.start('index.html', options=options, block=False)
	# interface.port
	print('Started WebUI!')
	if browser:
		print('Awaiting connection from browser...')
	else:
		print('Browser auto-opening is disabled! Please open a browser to http://%s:%s/index.html !' %
			  (options['host'], options['port']))
	return True


def _websocket_close():
	print('A WebUI just closed.')
	eel.sleep(1.0)
	if len(eel._websockets) == 0 and not settings.get('interface.keep_open'):
		print('WebUI keep_open is disabled, and all open clients have closed.\nExiting.')
		sys.exit()
eel._websocket_close = _websocket_close


@eel.btl.route('/file')
def _downloaded_files():
	""" Allows the UI to request files RMD has scraped.
		In format: "./file?id=Path/to/File.jpg"
	"""
	file_path = eel.btl.request.query.id
	print(f'Requested RMD File: {file_path}')
	return eel.btl.static_file(file_path, root=_file_dir)


# ======  JS->Python API functions:  ======
@eel.expose
def api_current_status(a, b):
	print('Eel api call:', a, b, a + b)  # TODO: once WebUI is passed 'main', implement progress status here.
	return a + b

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



if __name__ == '__main__':
	settings.load('test-webui-settings.json')
	opened = start('../../web/', '../../../download')
	while opened:
		eel.sleep(60)
