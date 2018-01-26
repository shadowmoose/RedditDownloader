import stringutil
from colorama import Fore, Style
import os
import hashjar

class ElementProcessor:
	""" The heavy-lifting bit. Handles processing all the Elements provided to it via the generator it's created with, by finding the most appropriate Handler for each Element. """
	
	def __init__(self, reddit_loader, settings, manifest):
		""" Creates and prepares the Processor object, with the given RedditLoader to provide RedditElements. Takes a loaded Settings object to find the configured save path. """
		self.loader = reddit_loader
		self.gen = self.loader.get_elements()
		self.settings = settings
		self.manifest = manifest
		self.handlers = []
		self.load_handlers()
	#
	
	def load_handlers(self):
		""" Loads all the available handlers from the handler directory. """
		self.handlers = []
		for mod in os.listdir('classes/handlers'):
			if mod == '__init__.py' or mod[-3:] != '.py':
				continue
			lib = __import__(mod[:-3], locals(), globals())
			self.handlers.append(lib)
		#
		self.handlers.sort(key=lambda x: x.order, reverse=False)
		print("Loaded handlers: ", ', '.join([x.tag for x in self.handlers]) )
		assert len(self.handlers)>0
	#
	
	def run(self):
		for ele in self.gen:
			self.process_ele(ele)
	#
	
	
	def process_ele(self, reddit_element):
		""" Accepts a RedditElement of Post/Comment details, then runs through the Handlers loaded from the other directory, attempting to download the url.  """
		print('%i/%i: ' % (self.loader.count_completed()+1, self.loader.count_total() ), end='')
		stringutil.print_color(Fore.LIGHTYELLOW_EX, stringutil.out("[%s](%s): %s" % (reddit_element.type, reddit_element.subreddit, reddit_element.title), False))

		for url in reddit_element.get_urls():
			print('\tURL: %s' % url)
			file = self.loader.url_exists(url)
			if file:
				stringutil.print_color(Fore.GREEN, "\t\t+URL already taken care of.")
				reddit_element.add_file(url, file)
				continue
			if self.manifest:
				skip, file = self.manifest.url_completed(url)
				if skip and (file is None or os.path.exists(file)):
					stringutil.print_color(Fore.GREEN, "\t\t+URL already handled in previous run.")
					reddit_element.add_file(url, file)
					if file is not None:
						hashjar.add_hash(file) # Add the existing file hash so we can deduplicate against it.
					continue
			file_info = self.build_file_info(reddit_element)# Build the file information dict using this RedditElement's information
			if file_info is None:
				file_path = False # If an error occurs during the generation of this file information.
			else:
				file_path = self.process_url(url, file_info)
			reddit_element.add_file(url, self.check_duplicates(file_path))
	#


	def process_url(self, url, info):
		""" Accepts a URL and the array of file info generated for it by this class, and then attempts to download it using any possible handler.
			Returns whatever the handlers do, which should be a path to the file itself or the containing directory for an album.
				+Also returns False or None if no appropriate handler was found, or if the handler told us not to download anything.
		"""
		ret_val = False # Default to 'False', meaning no file was located by a handler.
		for h in self.handlers:
			print("\tChecking handler: %s" % h.tag)
			ret = h.handle(url, info)
			if ret is None:
				# None is returned when the handler specifically wants this URL to be "finished", but not added to the files list.
				stringutil.print_color(Fore.GREEN, "\t+Handler '%s' completed correctly, but returned no files!" % h.tag )
				ret_val = None
				break
			if ret:
				# The handler will return a file/directory name if it worked properly.
				ret_val = stringutil.normalize_file(ret)
				stringutil.out("%s\t+Handler '%s' completed correctly! %s%s" % (Fore.GREEN, h.tag, stringutil.fit(ret_val, 75), Style.RESET_ALL) )
				break
			#
		#
		if ret_val is False:
			stringutil.error("\t!No handlers were able to accept this URL." )
		return ret_val
	#


	def build_file_info(self, reddit_element):
		""" Generates a dict of file locations and element data that is passed down to every handler, so they can choose where best to save for themselves. """
		dir_pattern  = '%s/%s' % ( self.settings.save_base() , self.settings.save_subdir() )
		file_pattern = '%s/%s' % ( dir_pattern, self.settings.save_filename())
		
		basedir = stringutil.insert_vars(dir_pattern, reddit_element)
		basefile = stringutil.insert_vars(file_pattern, reddit_element)

		if basedir is None or basefile is None:
			stringutil.error("\tCannot download this file, because the file path generated for it is too long!")
			stringutil.error("\tTry cutting back on the subdirectory length!")
			return None
		
		og = basefile
		i=2
		while self.loader.file_exists(basefile) or reddit_element.contains_file(basefile):
			print("\t!Incrementing duplicate filename. (%s)" % i, end='\r')
			basefile = og+' . '+str(i)+' '
			i+=1
		if i>2:
			print('')

		# Build an array of pre-generated possible locations & important data for handlers to have access to.
		return {
			'parent_dir'	: basedir,			# Some handlers will need to build the parent directory for their single file first. This simplifies parsing.
			'single_file'	: basefile+"%s",	# If this handler can output a single file, it will use this path.
			'multi_dir' 	: basefile+"/",		# If the handler is going to download multiple files, it will save them under this directory.
			'post_title'	: reddit_element.title,			# The title of the Reddit post.
			'post_subreddit': reddit_element.subreddit,		# The subreddit this post came from.
			'user_agent'	: self.settings.get('auth', None)['user_agent'],
		}


	def check_duplicates(self, file_path):
		""" Check the given file path to see if another file like it already exists. Purges worse copies.
			Returns the filename that the file exists under.
		"""
		if not file_path:
			return file_path
		if not self.settings.get('deduplicate_files', True):
			# Deduplication disabled.
			return file_path
		was_new, existing_path = hashjar.add_hash(file_path) # Check if the file exists already.
		if not was_new:
			print("\tFile already exists! Resolving...")
			# Quick and dirty comparison, assumes larger filesize means better quality.
			if os.path.isfile(file_path) and os.path.isfile(existing_path):
				if os.path.getsize(file_path) > os.path.getsize(existing_path):
					print('\t\tNew file was better quality. Removing old file.')
					os.remove(existing_path)
					for ele in self.loader.get_elements_for_file(existing_path):
						ele.remap_file(existing_path, file_path)
					return file_path
				else:
					print("\tOld file was better quality, removing newer file.")
					os.remove(file_path)
					return existing_path
		return file_path
