import eel
import sys
import os
import filters
import sources
from static import settings
from static import praw_wrapper
from static import metadata
from interfaces import UserInterface
from processing.wrappers import SanitizedRelFile
from processing.controller import RMDController
import sql

"""
	Eel is great, but doesn't expose everything we want.
	So by locking Eel to specific versions, we can easily override whatever we need here.
	
	See simple documentation: https://bottlepy.org/docs/dev/tutorial.html
"""


class WebUI(UserInterface):
	def __init__(self):
		super().__init__(ui_id="web")

	def display(self):
		if started:
			return False
		webdir = os.path.join(os.path.dirname(__file__), '../web/')
		start(web_dir=webdir)
		while not stopped:
			eel.sleep(1)

	@property
	def running(self):
		return started and not stopped

	def waitFor(self, max_time=10):
		for i in range(max_time*10):
			sleep(.1)
			if self.running:
				return True
		return False


started = False
stopped = False
_web_dir = None
_controller: RMDController = None
_session = None
_stat_cache = None


def start(web_dir):
	global _web_dir, started, _session
	_web_dir = os.path.abspath(web_dir)
	_session = sql.session()
	if not settings.get('interface.start_server'):
		print('WebUI is disabled by settings.')
		return False
	browser = settings.get('interface.browser').lower().strip()
	browser = None if (browser == 'off') else browser
	options = {
		'app_mode': '-app' in browser if browser else None,
		'mode': browser.replace('-app', '') if browser else None,
		'host': settings.get('interface.host'),
		'port': settings.get('interface.port'),
		'block': False,
		'close_callback': _websocket_close,
		'all_interfaces': False,
		# 'app': btl.default_app()
	}

	eel.init(web_dir)
	eel.start('index.html', **options)
	print('Started WebUI!')
	if browser:
		print('Awaiting connection from browser...')
	else:
		print('Browser auto-opening is disabled! Please open a browser to http://%s:%s/index.html !' %
			  (options['host'], options['port']))
	started = True
	return True


def _websocket_close(page, old_websockets):
	global stopped
	print('A WebUI just closed. Checking for other connections... (%s)[%s]' % (page, len(old_websockets)))
	for i in range(40):
		eel.sleep(.1)
		# noinspection PyProtectedMember
		if len(eel._websockets) > 0:
			print('Open connections still exist. Not stopping UI server.')
			return
	if not settings.get('interface.keep_open'):
		print('WebUI keep_open is disabled, and all open clients have closed. Exiting.')
		if _controller and _controller.is_alive():
			_controller.stop()
		stopped = True
	else:
		print('Keeping UI server open...')


def get_cached_stats():
	""" Track and cache misc stats for RMD. Cache is invalidated when downloading starts. """
	global _stat_cache
	if not _stat_cache:
		_stat_cache = {
			'total_files': _session.query(sql.File).count(),
			'total_files_dl': _session.query(sql.File).filter(sql.File.downloaded).count(),
			'total_submissions': _session.query(sql.Post).filter(sql.Post.type == 'Submission').count(),
			'total_comments': _session.query(sql.Post).filter(sql.Post.type == 'Comment').count(),
			'total_urls': _session.query(sql.URL).filter(sql.URL.processed).count(),
			'total_urls_failed': _session.query(sql.URL).filter(sql.URL.failed).count()
		}
	return _stat_cache


@eel.btl.route('/file')
def _downloaded_files():
	""" Allows the UI to request files RMD has scraped.
		In format: "./file?id=file_token"
	"""
	token = eel.btl.request.query.id
	file_obj = _session.query(sql.File).filter(sql.File.id == token).first()
	file_path = file_obj.path
	print('Requested RMD File: %s, %s' % (settings.get("output.base_dir"), file_path))
	response = eel.btl.static_file(file_path, root=os.path.abspath(settings.get("output.base_dir")))
	response.set_header("Cache-Control", "public, max-age=0")
	return response


@eel.btl.route('/authorize')
def _authorize_rmd_token():
	state = eel.btl.request.query.state
	print('New refresh code request: ', state, eel.btl.request.query.code)
	if state.strip() == settings.get('auth.oauth_key').strip():
		code = eel.btl.request.query.code
		print('Saving new reddit code.')
		refresh = praw_wrapper.get_refresh_token(code)
		if refresh:
			settings.put('auth.refresh_token', refresh)
			return 'Saved authorization token! Close this page to continue.'
	return 'Cannot save the new auth key, something went wrong.<br><a href="../index.html">Back</a>'


# ======  JS->Python API functions:  ======
@eel.expose
def api_current_status():
	return {'current_version': metadata.current_version}


@eel.expose
def api_get_oauth_url():
	port = 7505
	url = False
	message = ''
	if settings.get('interface.port') != port:
		message = 'The UI is not using the default port (%s), and cannot use the Web App to authenticate! ' \
				  'Run RMD with "--authorize" to manually authenticate!' % port
	else:
		url = praw_wrapper.get_reddit_token_url()
	return {
		'url': url,
		'message': message
	}


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
	for s in sources.load_sources():
		ret['available'].append(s.to_obj(for_webui=True))
	for s in settings.get_sources():
		ret['active'].append(s.to_obj(for_webui=True))
	ret['filters']['available'] = [f.to_js_obj() for f in filters.get_filters()]
	ret['filters']['operators'] = [f.value for f in filters.Operators]
	return ret


@eel.expose
def api_save_sources(new_obj):
	print('Saving new source list:')
	output_settings = []
	for so in new_obj:
		print('\tType:', so['type'], 'Alias:', so['alias'], so['filters'])
		for s in sources.load_sources():
			if s.type == so['type']:
				s.set_alias(so['alias'])
				for k, v in so['data'].items():
					s.insert_data(k, v)
				for f in so['filters']:
					for fi in filters.get_filters():
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
	return sql.PostSearcher(_session).get_searchable_fields()


@eel.expose
def api_search_posts(fields, term, page_size, page):
	print('Searching posts:', fields, term, page_size, page)
	ret = []
	searcher = sql.PostSearcher(_session)
	res = searcher.search_fields(fields, term.strip("%"))
	full_len = len(res)
	res = res[page*page_size:page*page_size+page_size]
	for p in res:
		files = []
		for url in p.urls:
			if not url.file:
				print('Post URL Missing a File:', url)
				continue
			file = SanitizedRelFile(base=settings.get("output.base_dir"), file_path=url.file.path)
			if file.is_file():
				files.append({'token': url.file.id, 'path': file.absolute()})
		if len(files):
			ret.append({
				'reddit_id': p.reddit_id,
				'author': p.author,
				'type': p.type,
				'title': p.title,
				'body': p.body,
				'parent_id': p.parent_id,
				'subreddit': p.subreddit,
				'over_18': p.over_18,
				'created_utc': p.created_utc,
				'num_comments': p.num_comments,
				'score': p.score,
				'source_alias': p.source_alias,
				'files': files
			})
	print('returned:', len(ret))
	return {
		'total': full_len,
		'results': ret
	}


@eel.expose
def api_shutdown():
	""" Terminates Python. """
	sys.exit(0)


@eel.expose
def start_download():
	global _controller, _stat_cache
	if _controller is not None and _controller.is_running():
		return False
	else:
		_controller = RMDController()
		_controller.start()
		_stat_cache = None
		print('Started downloader.')
		return True


@eel.expose
def download_status():
	if _controller is None or not _controller.is_alive():
		return {
			'running': False,
			'summary': get_cached_stats()
		}
	return _controller.get_progress().to_obj()


@eel.expose
def get_failed():
	fails = _session\
		.query(sql.Post)\
		.join(sql.URL)\
		.filter(sql.URL.failed == True)\
		.all()
	return sql.encode_safe(fails)


@eel.expose
def get_authed_user():
	# noinspection PyBroadException
	try:
		return praw_wrapper.get_current_username()
	except Exception as ex:
		return None


def sleep(sec):
	eel.sleep(sec)
