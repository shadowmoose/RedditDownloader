# noinspection PyPackageRequirements
from newspaper import Article, Config
import requests
import mimetypes
import shutil
from handlers import HandlerResponse
from static import settings

tag = 'newspaper'
order = 90000

""" This is (one of) the last-ditch handlers. 
	If all else fails, we attempt to use the Newspaper library to extract the top image from whatever site. 
	
	Is it better to fail sometimes, or to get the wrong parse instead?
	This library will almost *certainly* find something to download, even if that image is a really bad option.
	Still, though, it works on sites like Tumblr and other really fringe pages, 
	so it's probably worthwhile to be correct more often than not.
	Return filename/directory name of created file(s),
	False if a failure is reached, or None if there was no issue, but there are no files.
"""


def handle(task, progress):
	user_agent = settings.get('auth.user_agent')
	url = task.url
	progress.set_status("Requesting page...")
	resp = requests.get(url, headers={'User-Agent': user_agent})
	if resp.status_code != 200:
		return False  # !cover

	config = Config()
	config.memoize_articles = False
	config.verbose = False
	article = Article(url='', config=config)

	article.download()
	article.set_html(resp.text)
	article.parse()
	if not article.top_image:
		return None

	src = article.top_image
	if 'http' not in src:  # !cover
		if 'https' in url:
			src = 'https://' + src.lstrip('/ ').strip()
		else:
			src = 'http://' + src.lstrip('/ ').strip()

	progress.set_status("Downloading image...")

	r = requests.get(src, headers={'User-Agent': user_agent}, stream=True)
	if r.status_code == 200:
		content_type = r.headers['content-type']
		ext = mimetypes.guess_extension(content_type)
		if not ext or ext == '':  # !cover
			return None
		if '.jp' in ext:
			ext = '.jpg'  # !cover

		task.file.set_ext(ext)
		task.file.mkdirs()
		progress.set_file(task.file.relative())
		with open(task.file.absolute(), 'wb') as f:
			r.raw.decode_content = True
			shutil.copyfileobj(r.raw, f)
		return HandlerResponse(success=True, rel_file=task.file, handler=tag)
	else:  # !cover
		# log.out(0, ('\t\tError Reading Image: %s responded with code %i!' % (url, r.status_code)))
		return None
