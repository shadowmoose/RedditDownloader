import re
import os
import math
from collections import Counter
import requests
import mimetypes
import shutil
import urllib.parse
import stringutil

tag = 'imgur'
order = 1

# TODO: This class needs some major refactoring. The library is fine, but the single-image handler needs splitting.

"""
imguralbum.py - Download a whole imgur album in one go.
Provides both a class and a command line utility in a single script
to download Imgur albums.
MIT License
Copyright Alex Gisby <alex@solution10.com>
"""

# Pulled from: https://github.com/alexgisby/imgur-album-downloader and modified.

class ImgurAlbumException(Exception):
	def __init__(self, msg='Error'):
		self.msg = msg


class ImgurAlbumDownloader:
	def __init__(self, album_url, user_agent=""):
		"""
		Constructor. Pass in the album_url that you want to download.
		"""
		self.album_url = album_url

		# Callback members:
		self.image_callbacks = []
		self.complete_callbacks = []
		
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
			self.response = requests.get(full_list_url, headers = {'User-Agent': self.user_agent})
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
		self.imageIDs =  [x for x in self.imageIDs if x not in seen and not seen.add(x)]
		self.cnt = Counter()
		for i in self.imageIDs:
			self.cnt[i[1]] += 1


	def num_images(self):
		"""
		Returns the number of images that are present in this album.
		"""
		return len(self.imageIDs)


	def list_extensions(self):
		"""
		Returns list with occurrences of extensions in descending order.
		"""  
		return self.cnt.most_common()


	def album_key(self):
		"""
		Returns the key of this album. Helpful if you plan on generating your own
		folder names.
		"""
		return self.album_key
	
	def set_path(self, path):
		"""
		Overrides the generated paths to use this one for all images, 
		Automatically appending the file extension.
		"""
		self.custom_path = path

	def on_image_download(self, callback):
		"""
		Allows you to bind a function that will be called just before an image is
		about to be downloaded. You'll be given the 1-indexed position of the image, its URL
		and its destination file in the callback like so:
			my_awesome_callback(1, "http://i.imgur.com/fGWX0.jpg", "~/Downloads/1-fGWX0.jpg")
		"""
		self.image_callbacks.append(callback)


	def on_complete(self, callback):
		"""
		Allows you to bind onto the end of the process, displaying any lovely messages
		to your users, or carrying on with the rest of the program. Whichever.
		"""
		self.complete_callbacks.append(callback)


	def save_images(self, foldername=False):
		"""
		Saves the images from the album into a folder given by foldername.
		If no foldername is given, it'll use the cwd and the album key.
		And if the folder doesn't exist, it'll try and create it.
		"""
		# Try and create the album folder:
		if foldername:
			album_folder = foldername
		else:
			album_folder = self.album_key

		if not os.path.exists(album_folder):
			os.makedirs(album_folder)

		# And finally loop through and save the images:
		for (counter, image) in enumerate(self.imageIDs, start=1):
			image_url = "http://i.imgur.com/"+image[0]+image[1]

			prefix = "%0*d-" % (
				int(math.ceil(math.log(len(self.imageIDs) + 1, 10))),
				counter
			)

			if self.custom_path:
				self.custom_path+= image[1]
				path = self.custom_path
			else:
				path = os.path.join(album_folder, prefix + image[0] + image[1])

			# Run the callbacks:
			for fn in self.image_callbacks:
				fn(counter, image_url, path)

			# Actually download the thing
			if not os.path.isfile(path):
				try:
					#urllib.request.urlretrieve(image_url, path)
					r = requests.get(image_url, headers = {'User-Agent': self.user_agent}, stream=True)
					if r.status_code != 200:
						stringutil.error("Failed to download image! [%i]" % r.status_code )
						raise ImgurAlbumException("Error reading Imgur Image: Error Code %d" % r.status_code)
					with open(path, 'wb') as f:
						r.raw.decode_content = True
						shutil.copyfileobj(r.raw, f)
				except KeyboardInterrupt:
					raise
				except:
					print ("Imgur Download failed.")
					if os.path.isfile(path):
						os.remove(path)
					raise

		# Run the complete callbacks:
		for fn in self.complete_callbacks:
			fn()


# Return filename/directory name of created file(s), False if a failure is reached, or None if there was no issue, but there are no files.
def handle(url, data, guess=True):
	if 'imgur' not in url:
		return False
		
	# Not a gallery, so we have to do our best to manually find/format this image.
	if not any(x in url for x in ['gallery', '/a/']):
		# If we've got a non-gallery, and missing the direct image url, correct to the direct image link.
		if 'i.img' not in url:
			base_img = url.split("/")[-1]
			req = requests.get(url, headers = {'User-Agent': data['user_agent']})
			if 'i.img' in req.url:
				# Redirected to valid Image.
				url = req.url
				print("\t\t+Auto-corrected Imgur URL: %s" % url)
			else:
				# Load the page and parse for image.
				for u in stringutil.html_elements(req.text, 'img', 'src'):
					if base_img in u:
						u = urllib.parse.urljoin('https://i.imgur.com/', u)
						print("\t\t+Corrected Imgur URL: %s" % u)
						url = u
						break
		
		# Handle the direct imgur links, because the lib doesn't.
		if 'i.imgur.com' in url:
			path = None
			try:
				# I don't like that we basically end up loading every image just to skip some,
				# but it's best to verify filetype with imgur, because the URL can ignore extension.
				r = requests.get(url, headers = {'User-Agent': data['user_agent']}, stream=True)
				if r.status_code == 200:
					content_type = r.headers['content-type']
					ext = mimetypes.guess_extension(content_type)
					if 'gifv' in url:
						print('\t\t-Allowing YTDL Handler to download animations.')
						return False# Let Youtube-dl module convert animations.
					if not ext or ext=='':
						stringutil.error('\t\tError locating file MIME Type: %s' % url)
						if guess:
							# Attempt to download this image (missing a file ext) as a png.
							# It's last-ditch, but works in some cases.
							return handle(url+'.png', data, False)
						else:
							return False
					
					if '.jp' in ext:
						ext = '.jpg'
					path = data['single_file'] % ext
					
					if not os.path.isfile(path):
						if not os.path.isdir(data['parent_dir']):
							print("\t\t+Building dir: %s" % data['parent_dir'])
							os.makedirs(data['parent_dir'])# Parent dir for the full filepath is supplied already.
						
						with open(path, 'wb') as f:
							r.raw.decode_content = True
							shutil.copyfileobj(r.raw, f)
							return path
					else:
						return path
				else:
					stringutil.error('\t\tError Reading Image: %s responded with code %i!' % (url, r.status_code) )
					return False
			except KeyboardInterrupt:
				raise
			except Exception as e:
				stringutil.error("\t\t"+str(e) )
				stringutil.error("\t\tError downloading direct Image: [%s] to path [%s]" % (url, path))
				if path and os.path.isfile(path):
					os.remove(path)
			stringutil.error('\t\tSomething strange failed with direct Imgur download...')
			return False
	else:
		if 'i.' in url:
			# Sometimes people include 'i.imgur' in album releases, which is incorrect.
			# Imgur redirects this, but we correct for posterity.
			url = url.replace('i.', '')
	#
	try:
		# Fire up the class:
		downloader = ImgurAlbumDownloader(url, data['user_agent'])
		print(("\t\tFound {0} images in album".format(downloader.num_images())))
		
		ret = data['multi_dir']# Create with a default value, assumes we're getting multiple files.
		targ_dir = data['multi_dir']# We're either downloading to a multi-dir, or the parent "subreddit" dir.
		if downloader.num_images() == 1:
			downloader.set_path(data['single_file'] % '')
			targ_dir = data['parent_dir']
		
		def print_image_progress(index, img_url, dest):
			crop = stringutil.fit(dest, 75)
			print("\t\tDownloading Image %d	%s >> %s" % (index, img_url, crop), end='\r')
		#
		downloader.on_image_download(print_image_progress)
		
		downloader.save_images(targ_dir)
		print("\n\t\tImgur download complete!")
		if downloader.num_images() == 1:
			# if there's only a single image, the downloader auto-modifies this to include
			# the image extension after saving the single file.
			ret = downloader.custom_path

		return ret
	except ImgurAlbumException as e:
		stringutil.error("\t\tImgur Error: "+e.msg)
	return False