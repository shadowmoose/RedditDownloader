# noinspection PyPackageRequirements
from newspaper import Article, Config
from processing.wrappers import http_downloader

tag = 'newspaper'
order = 90000

""" This is (one of) the last-ditch handlers. 
	If all else fails, we attempt to use the Newspaper library to extract the top image from whatever site. 
	
	Is it better to fail sometimes, or to get the wrong parse instead?
	This library will almost *certainly* find something to download, even if that image is a really bad option.
	Still, though, it works on sites like Tumblr and other really fringe pages, 
	so it's probably worthwhile to be correct more often than not.
"""


def handle(task, progress):
	url = task.url
	progress.set_status("Requesting page...")
	resp = http_downloader.page_text(url, json=False)
	if not resp:
		return False

	config = Config()
	config.memoize_articles = False
	config.verbose = False
	article = Article(url='', config=config)

	article.download()
	article.set_html(resp)
	article.parse()
	if not article.top_image:
		return None

	src = article.top_image
	if 'http' not in src:
		if 'https' in url:
			src = 'https://' + src.lstrip('/ ').strip()
		else:
			src = 'http://' + src.lstrip('/ ').strip()

	progress.set_status("Downloading image...")

	return http_downloader.download_binary(src, task.file, prog=progress, handler_id=tag)
