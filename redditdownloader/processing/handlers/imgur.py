import re
import urllib.parse
from static import stringutil
from processing.handlers import HandlerResponse
from processing.wrappers import http_downloader

tag = 'imgur'
order = 1


imgur_animation_exts = ['.mp4', '.webm', '.gifv']


# Code borrowed from: https://github.com/alexgisby/imgur-album-downloader and modified.
class ImgurAlbumException(Exception):
	def __init__(self, msg='Error'):  # !cover
		self.msg = msg


class ImgurAlbumDownloader:
	def __init__(self, album_url):
		"""
		Constructor. Pass in the album_url that you want to download.
		"""
		self.album_url = album_url

		# Check the URL is actually imgur:
		match = re.match("(https?)://(www\.)?(?:m\.)?imgur\.com/(a|gallery)/([a-zA-Z0-9]+)(#[0-9]+)?", album_url)
		if not match:
			raise ImgurAlbumException("URL must be a valid Imgur Album")

		self.protocol = match.group(1)
		self.album_key = match.group(4)
		self.custom_path = None
		
		# Read the no-script version of the page for all the images:
		full_list_url = "https://imgur.com/a/" + self.album_key + "/layout/blog"

		html = http_downloader.page_text(full_list_url)

		if not html:
			raise ImgurAlbumException("Error reading Imgur Album Page: %s" % full_list_url)

		self.imageIDs = re.findall('.*?{"hash":"([a-zA-Z0-9]+)".*?"ext":"(\.[a-zA-Z0-9]+)".*?', html)
		seen = set()
		self.urls = ["https://i.imgur.com/" + x[0]+x[1] for x in self.imageIDs if x not in seen and not seen.add(x)]

	def get_urls(self):
		return list(self.urls)


def get_direct_link(url):
	"""
	If we've got a non-gallery, and missing the direct image url, correct to the direct image link.
	"""
	if is_direct_link(url):
		return url
	base_img = url.split("/")[-1]
	req = http_downloader.open_request(url, stream=False)
	if 'i.img' in req.url:
		# Redirected to valid Image.
		return req.url
	else:
		# Load the page and parse for image.
		possible_eles = [('link', 'href'), ('img', 'src')]
		for pe in possible_eles:
			for u in stringutil.html_elements(req.text, pe[0], pe[1]):
				if is_direct_link(u, base_img):
					return urllib.parse.urljoin('https://i.imgur.com/', u)
		# Check for embedded video:
		possible_eles = [('meta', 'content'), ('source', 'src')]
		for pe in possible_eles:
			for u in stringutil.html_elements(req.text, pe[0], pe[1]):
				if is_direct_link(u, base_img) and any((ext in u) for ext in imgur_animation_exts):
					return urllib.parse.urljoin('https://i.imgur.com/', u)
	return None


def is_direct_link(url, base_img=''):
	""" Check if the given URL matches an expected direct Imgur URL. """
	return base_img in url \
		   and 'i.imgur' in url \
		   and 'api.' not in url \
		   and '?' not in url \
		   and '.' in url.split('/')[-1]


def clean_imgur_url(url):
	""" Attempts to - very generously - clean the given URL into a valid Imgur location. Returns the url, if valid. """
	url = url.lstrip(':/').replace('m.imgur.', 'imgur.')
	if not url.startswith('http'):
		url = 'https://%s' % url
	if re.match("^(?:https?[:/]*)?(?:www.)?(?:[mi]\.)?imgur\.com/", url):
		return url
	return False


def handle(task, progress):
	url = clean_imgur_url(task.url)
	if not url:
		return False
	direct_url = url.replace('/gallery/', '/').replace('/a/', '/')

	progress.set_status("Parsing url & verifying format...")

	album_exception = None

	# Check for an album/gallery.
	if any(x in url for x in ['gallery', '/a/']):
		if 'i.' in url:
			# Imgur redirects this, but we correct for posterity.
			url = url.replace('i.', '')
		try:
			album = ImgurAlbumDownloader(url)
			return HandlerResponse(success=True, handler=tag, album_urls=album.get_urls())
		except ImgurAlbumException as ex:
			album_exception = ex
			pass  # It's possible an image incorrectly has a Gallery location, which Imgur can resolve. Try direct dl:

	url = get_direct_link(direct_url)

	if not url:
		if album_exception:
			print("ImgurAlbumException:", album_exception)
		return False  # Unable to parse proper URL.
	return http_downloader.download_binary(url, task.file, prog=progress, handler_id=tag)


