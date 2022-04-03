import re
from processing.wrappers import http_downloader

tag = 'redgifs'
order = 1

""" 
	This Handler attempts to convert Gyfcat links into direct video links.
"""

format_opts = ["webmUrl", "mp4Url", "gifUrl"]


def handle(task, progress):
	url = task.url
	try:
		redgif_id = re.match(r'.*/(.*?)/?$', url).group(1)
	except AttributeError:
		return False

	 headers = {
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
		'Chrome/90.0.4430.93 Safari/537.36',}

		content = Redgifs.retrieve_url(f'https://api.redgifs.com/v2/gfycats/{redgif_id}', headers=headers)

		if content is None:
			return False

		try:
			out = json.loads(content.text)['gif']['urls']["gif"]
		except (KeyError, AttributeError):
			return False
		except json.JSONDecodeError as e:
			return False
	progress.set_status("Downloading from redgifs..." % opt)
	return http_downloader.download_binary(out, task.file, prog=progress, handler_id=tag)
