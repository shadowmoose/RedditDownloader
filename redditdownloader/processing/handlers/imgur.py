import re
import urllib.parse as urlp
from os.path import splitext, basename
from processing.handlers import HandlerResponse
from processing.wrappers import http_downloader
from imgurpython import ImgurClient
from static import settings


tag = 'imgur'
order = 1

imgur_animation_exts = ['mp4', 'webm', 'gif', 'gifv']
_imgur_client = None


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
		match = re.match(r"(https?)://(www\.)?(?:m\.)?imgur\.com/(a|gallery)/([a-zA-Z0-9]+)(#[0-9]+)?", album_url)
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

		self.imageIDs = re.findall(r'.*?{"hash":"([a-zA-Z0-9]+)".*?"ext":"(\.[a-zA-Z0-9]+)".*?', html)
		seen = set()
		self.urls = ["https://i.imgur.com/" + x[0] + x[1] for x in self.imageIDs if x not in seen and not seen.add(x)]

	def get_urls(self):
		return list(self.urls)


def make_api_client():
	global _imgur_client
	client_id = settings.get('imgur.client_id')
	client_secret = settings.get('imgur.client_secret')
	if not _imgur_client and client_id and client_secret:
		_imgur_client = ImgurClient(client_id, client_secret)
	return _imgur_client


def parse_url(url):
	url = url.lstrip(':/')
	if not url.startswith('http'):
		url = 'https://' + url
	return urlp.urlparse(url)


def is_imgur(url):
	sp = parse_url(url)
	tloc = '.'.join(sp.netloc.split('.')[-2:])
	return tloc == 'imgur.com'


def is_gallery(url):
	sp = parse_url(url)
	return sp.path and any(sp.path.startswith(x) for x in ['/a/', '/gallery/'])


def build_direct_link(url):
	sp = parse_url(url)
	filename, ext = splitext(basename(sp.path))
	if not ext:
		ext = '.png'  # Guess the type: Imgur will auto-resolve to the direct image, even if the extension is wrong.
	if ext == '.gifv':
		ext = '.mp4'
	return urlp.urljoin('https://i.imgur.com/', '%s%s' % (filename, ext))


def extract_id(url):
	sp = parse_url(url)
	filename, ext = splitext(basename(sp.path))
	return filename


def handle(task, progress):
	url = task.url
	if not is_imgur(url):
		return False

	# Check for an album/gallery.
	if is_gallery(url):
		if 'i.' in url:
			# Imgur redirects this, but we correct for posterity.
			url = url.replace('i.', '')
		urls = []
		try:
			album = ImgurAlbumDownloader(url)
			urls = album.get_urls()
		except ImgurAlbumException:
			pass  # It's possible an image incorrectly has a Gallery location prepended. Ignore error.

		if not len(urls):  # Try using the imgur API to locate this album.
			try:
				# fallback to imgur API client, if enabled, for hidden albums.
				client = make_api_client()
				if not client:
					return HandlerResponse(success=False,
										   handler=tag,
										   failure_reason="Could not locate hidden album, and API client is disabled.")
				items = client.get_album_images(extract_id(url))

				def best(o):  # Find the best-quality link available within the given Imgur object.
					for b in ['mp4', 'gifv', 'gif', 'link']:
						if hasattr(o, b):
							return getattr(o, b)
				urls = [best(i) for i in items if not getattr(i, 'is_ad', False)]
			except Exception as e:
				print('Imgur API:', e)
				pass  # It's possible an image incorrectly has a Gallery location prepended. Ignore error.
		if len(urls) == 1:
			url = urls[0]  # For single-image albums, set up to directly download the image.
		elif len(urls):
			return HandlerResponse(success=True, handler=tag, album_urls=urls)

	url = build_direct_link(url)
	ext, stat = http_downloader.is_media_url(url, return_status=True)  # Do some pre-processing, mostly to screen filetypes.
	if not ext or stat != 200:
		return HandlerResponse(success=False,
							   handler=tag,
							   failure_reason="Unable to determine imgur filetype: HTTP %s: %s" % (stat, url))
	if ext in imgur_animation_exts:
		url = '.'.join(url.split('.')[:-1]) + '.mp4'
	return http_downloader.download_binary(url, task.file, prog=progress, handler_id=tag)
