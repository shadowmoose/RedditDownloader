import re
import os
import urllib.parse
from static import stringutil
from processing.handlers import HandlerResponse
from processing.wrappers import http_downloader

tag = 'imgur'
order = 1


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
		full_list_url = "http://imgur.com/a/" + self.album_key + "/layout/blog"

		html = http_downloader.page_text(full_list_url)

		if not html:
			raise ImgurAlbumException("Error reading Imgur Album Page: Error Code %s" % full_list_url)

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
	req = http_downloader.open_request(url, stream=False)
	if 'i.img' in req.url:
		# Redirected to valid Image.
		return req.url
	else:
		# Load the page and parse for image.
		possible_eles = [('link', 'href'), ('img', 'src')]
		for pe in possible_eles:
			for u in stringutil.html_elements(req.text, pe[0], pe[1]):
				if base_img in u and 'i.imgur' in u and 'api.' not in u:
					return urllib.parse.urljoin('https://i.imgur.com/', u)
	return None


def read_animation(url, rel_file, progress):
	page_text = http_downloader.page_text(url, json=False)
	if not page_text:
		return HandlerResponse(success=False, handler=tag, failure_reason="Unable to download animation source.")
	for u in stringutil.html_elements(page_text, 'source', 'src'):
		if 'i.imgur' in u and '.mp4' in u:
			url = urllib.parse.urljoin('https://i.imgur.com/', u)
			return http_downloader.download_binary(url, rel_file=rel_file, prog=progress, handler_id=tag)
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
			url = url.replace('i.', '')
		try:
			album = ImgurAlbumDownloader(url)
			return HandlerResponse(success=True, handler=tag, album_urls=album.get_urls())
		except ImgurAlbumException as ex:
			print('ImgurException:', ex)
			return None

	url = get_direct_link(url)

	if not url:
		return False  # Unable to parse proper URL.

	if any(_e in url for _e in ['gifv', 'webm']):
		return read_animation(url, task.file, progress)
	return http_downloader.download_binary(url, task.file, prog=progress, handler_id=tag)


if __name__ == '__main__':
	from processing.wrappers import SanitizedRelFile, DownloaderProgress
	import processing.handlers as handlers
	_dsk = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
	_path = SanitizedRelFile(base=_dsk, file_path='test-image')
	print(_path.absolute())
	_task = handlers.HandlerTask(url=input("Enter an Imgur URL to download: ").strip(), file_obj=_path)
	_prog = DownloaderProgress()
	resp = handle(_task, _prog)
	if resp:
		print(resp)
		if resp.album_urls:
			print('New URLS:', resp.album_urls)
	else:
		print("NO response!")
	print('Last Status:', _prog.get_status())
	print("Percent:", _prog.get_percent())

