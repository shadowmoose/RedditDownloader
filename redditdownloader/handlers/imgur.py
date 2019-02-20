import re
import os
import requests
import mimetypes
import shutil
import urllib.parse
from static import stringutil
from static import settings
from handlers import HandlerResponse

tag = 'imgur'
order = 1


# Code borrowed from: https://github.com/alexgisby/imgur-album-downloader and modified.
class ImgurAlbumException(Exception):
	def __init__(self, msg='Error'):  # !cover
		self.msg = msg


class ImgurAlbumDownloader:
	def __init__(self, album_url, user_agent=""):
		"""
		Constructor. Pass in the album_url that you want to download.
		"""
		self.album_url = album_url
		
		self.user_agent = user_agent

		# Check the URL is actually imgur:
		match = re.match("(https?)://(www\.)?(?:m\.)?imgur\.com/(a|gallery)/([a-zA-Z0-9]+)(#[0-9]+)?", album_url)
		if not match:
			raise ImgurAlbumException("URL must be a valid Imgur Album")

		self.protocol = match.group(1)
		self.album_key = match.group(4)
		self.custom_path = None
		
		# Read the no-script version of the page for all the images:
		full_list_url = "http://imgur.com/a/" + self.album_key + "/layout/blog"

		try:
			self.response = requests.get(full_list_url, headers={'User-Agent': self.user_agent})
			response_code = self.response.status_code
		except requests.exceptions.RequestException:
			self.response = False
			response_code = -1

		if not self.response or response_code != 200:
			raise ImgurAlbumException("Error reading Imgur: Error Code %d" % response_code)

		# Read in the images now so we can get stats and stuff:
		html = self.response.text
		self.imageIDs = re.findall('.*?{"hash":"([a-zA-Z0-9]+)".*?"ext":"(\.[a-zA-Z0-9]+)".*?', html)
		seen = set()
		self.urls = ["http://i.imgur.com/" + x[0]+x[1] for x in self.imageIDs if x not in seen and not seen.add(x)]

	def get_urls(self):
		return list(self.urls)


def get_direct_link(url):
	"""
	If we've got a non-gallery, and missing the direct image url, correct to the direct image link.
	"""
	if 'i.img' in url:
		return url
	base_img = url.split("/")[-1]
	req = requests.get(url, headers={'User-Agent': settings.get('auth.user_agent')})
	if 'i.img' in req.url:
		# Redirected to valid Image.
		return req.url
	else:
		# Load the page and parse for image.
		for u in stringutil.html_elements(req.text, 'img', 'src'):
			if base_img in u:
				u = urllib.parse.urljoin('https://i.imgur.com/', u)
				return u
	return None


def handle(task, progress):
	url = task.url
	if 'imgur.com' not in url:
		return False

	progress.set_status("Parsing url & verifying format...")

	# Check for an album/gallery.
	if any(x in url for x in ['gallery', '/a/']):
		if 'i.' in url:
			# Imgur redirects this, but we correct for posterity.
			url = url.replace('i.', '')  # !cover
		try:
			album = ImgurAlbumDownloader(url, settings.get("auth.user_agent"))
			return HandlerResponse(success=True, handler=tag, album_urls=album.get_urls())
		except ImgurAlbumException:
			return None

	url = get_direct_link(url)

	if not url:
		return False  # Unable to parse proper URL.

	# noinspection PyBroadException
	try:
		# Verify filetype with imgur, because the URL can ignore extension.
		r = requests.head(url, headers={'User-Agent': settings.get('auth.user_agent')}, stream=True)
		if r.status_code != 200:
			return HandlerResponse(success=False,
								   handler=tag,
								   failure_reason="Imgur Server Error: %s->%s" % (url, r.status_code))

		content_type = r.headers['content-type']
		ext = mimetypes.guess_extension(content_type)
		if any(_e in url for _e in ['gifv', 'webm']):  # !cover
			return False  # TODO: YTDL is bad at these suddenly, so add custom handling here.
		if not ext or ext == '':  # !cover
			# stringutil.error('IMGUR: Error locating file MIME Type: %s' % url)
			return HandlerResponse(success=False, handler=tag, failure_reason="Unable to determine MIME Type: %s" % url)

		if '.jp' in ext:
			ext = '.jpg'  # !cover

		task.file.set_ext(ext)
		path = task.file.absolute()
		progress.set_status("Downloading image...")
		progress.set_file(task.file.relative())
		task.file.mkdirs()
		with open(path, 'wb') as f:
			r.raw.decode_content = True
			shutil.copyfileobj(r.raw, f)
		return HandlerResponse(success=True, rel_file=task.file, handler=tag)
	except Exception:
		if task.file.exists():
			os.remove(task.file.absolute())
		return None
