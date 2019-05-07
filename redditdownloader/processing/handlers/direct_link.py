from processing.wrappers import http_downloader
from processing.handlers import HandlerResponse

tag = 'direct_link'
order = 50

""" 
	This Handler attempts to find direct links to Media, not already handled by the other Handlers.
"""


def handle(task, progress):
	url = task.url
	progress.set_status("Checking for direct url...")
	ext, stat = http_downloader.is_media_url(url, return_status=True)

	if stat != 200:
		return HandlerResponse(success=False, handler=tag, failure_reason="URL Responded: %s" % stat)
	if not ext:
		return False

	progress.set_status("Downloading direct media...")
	return http_downloader.download_binary(url, task.file, prog=progress, handler_id=tag)
