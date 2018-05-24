import threading
import queue
import os
import pkgutil

import classes.processing.logger as logger
import classes.handlers as handlers
from classes.util import hashjar, stringutil
from classes.util import manifest
from classes.util import settings


class HandlerThread(threading.Thread):
	ele_lock = threading.RLock()
	used_files = [] # A shared list of used base filenames, to avoid duplicating files until they're written and stored.

	def __init__(self, name, e_queue):
		threading.Thread.__init__(self)
		self.name = name
		self.log = logger.Logger(2, padding=1)
		self.handler_log = logger.Logger(2, padding=2)
		self.handlers = []
		self.release_filenames = [] # Each thread keeps a list of base filenames it's currently using, to avoid dupes.

		self._loader = e_queue
		self.load_handlers()
		self.keep_running = True
		self.total_new_urls = 0  # Counter for stat display.
		self.total_new_posts = 0
		self.total_failed_urls = 0


	def run(self):
		self.log.out(0, 'Starting up.')
		while self.keep_running:
			self.log.out(0, "Waiting for queue...")
			self.handler_log.clear()
			try:
				item = self._loader.next_ele()
				if item is None:
					continue
				self.process_ele(item)
			except queue.Empty:
				self.keep_running = False
				# An exception is raised when queue is empty and loading is done.
				break
		self.log.out(0, stringutil.color('Completed.', stringutil.Fore.GREEN))
		self.handler_log.clear()
		self.keep_running = False


	def process_ele(self, reddit_element):
		""" Accepts a RedditElement of Post/Comment details, then runs through the Handlers loaded from the other directory, attempting to download the url.  """
		self.log.out(0, 'Processing new ele...')
		self.handler_log.clear()
		#print('\n\n\nProcessing ele: %s' % reddit_element.to_obj())
		self.log.out(0,
					 stringutil.out(
						 "[%s](%s): %s" % (reddit_element.type, reddit_element.subreddit, reddit_element.title),
						 False,
						 stringutil.Fore.LIGHTYELLOW_EX
					 )
		)
		was_new_ele = False
		for url in reddit_element.get_urls():
			was_new_url = True
			url_info  = manifest.get_url_info(url)
			if url_info:
				was_new_url = False  # The manifest has seen this URL before. It may have failed last time, though.
				file = url_info['file_path']
				if file and os.path.exists(file):
					#  This URL has already been handled, and its file still exists.
					reddit_element.add_file(url, file)
					hashjar.add_hash(file) # Update hash, just in case it doesn't have this file. (from legacy)
					continue

			was_new_ele = True
			# This URL hasn't been handled yet! Time to download it:
			file_info = self.build_file_info(reddit_element)# Build the file information dict using this RedditElement's information
			if file_info is None:
				reddit_element.add_file(url, False) # This mostly happens if the filename can't be generated.
			else:
				# Download file from new url, using the loaded Handlers:
				file_path = self.process_url(url, file_info)# The important bit is here, & doesn't need the Lock.
				if file_path:
					file_path = stringutil.normalize_file(file_path) # Normalize for all DB storage.
					if was_new_url:
						self.total_new_urls += 1
				else:
					self.total_failed_urls += 1
				if not self.keep_running:
					return # Kill the thread after a potentially long-running download if the program has terminated. !cover
				reddit_element.add_file(url, self.check_duplicates(file_path))

		manifest.insert_post(reddit_element) # Update Manifest with completed ele.
		if was_new_ele:
			self.total_new_posts += 1

		with HandlerThread.ele_lock:
			# Clear blacklisted filename list, just to release the memory.
			for r in self.release_filenames:
				HandlerThread.used_files.remove(r)
			self.release_filenames = []


	def build_file_info(self, reddit_element):
		""" Generates a dict of file locations and element data that is passed down to every handler, so they can choose where best to save for themselves. """
		with HandlerThread.ele_lock:
			dir_pattern  = './%s' % settings.save_subdir()
			file_pattern = '%s/%s' % ( dir_pattern, settings.save_filename())

			basedir = stringutil.insert_vars(dir_pattern, reddit_element)
			basefile = stringutil.insert_vars(file_pattern, reddit_element)

			if basedir is None or basefile is None:
				#Cannot download this file, because the file path generated for it is too long
				return None #!cover

			og = basefile
			i=2
			while basefile in HandlerThread.used_files:
				# Use local list of filenames used here, since used filenames won't be updated until done otherwise.
				basefile = og+' . '+str(i)
				basefile = stringutil.normalize_file(basefile)
				i+=1
			HandlerThread.used_files.append(basefile) # blacklist this base name while we download.
			self.release_filenames.append(basefile)

			# Build an array of pre-generated possible locations & important data for handlers to have access to.
			return {
				'parent_dir'	: basedir,			# Some handlers will need to build the parent directory for their single file first. This simplifies parsing.
				'single_file'	: basefile+"%s",	# If this handler can output a single file, it will use this path.
				'multi_dir' 	: basefile+"/",		# If the handler is going to download multiple files, it will save them under this directory.
				'post_title'	: reddit_element.title,			# The title of the Reddit post.
				'post_subreddit': reddit_element.subreddit,		# The subreddit this post came from.
				'user_agent'	: settings.get('auth.user_agent'),
			}
	# exit lock.


	def process_url(self, url, info):
		""" Accepts a URL and the array of file info generated for it by this class, and then attempts to download it using any possible handler.
			Returns whatever the handlers do, which should be a path to the file itself or the containing directory for an album.
				+Also returns False or None if no appropriate handler was found, or if the handler told us not to download anything.
		"""
		ret_val = False # Default to 'False', meaning no file was located by a handler.
		for h in self.handlers:
			self.log.out(1, stringutil.color("Checking handler: %s" % h.tag, stringutil.Fore.CYAN))
			ret = False

			# noinspection PyBroadException
			try:
				ret = h.handle(url, info, self.handler_log)
			except Exception:  # There are too many possible exceptions between all handlers to catch properly.
				pass  # Maybe consider stopping thread. I want to see errors reported, but don't want to interrupt users.

			if ret is None: #!cover
				# None is returned when the handler specifically wants this URL to be "finished", but not added to the files list.
				ret_val = None
				break
			if ret:
				# The handler will return a file/directory name if it worked properly.
				ret_val = stringutil.normalize_file(ret)
				break
		return ret_val


	def check_duplicates(self, file_path):
		""" Check the given file path to see if another file like it already exists. Purges worse copies.
			Returns the filename that the file now exists under.
		"""
		if not file_path:
			return file_path #!cover
		with HandlerThread.ele_lock:
			# The IO here could cause issues if multiple Threads tried to delete the same files, so safety lock.
			# Files currently downloading won't exist in the hashjar yet, so there's no risk of catching one in progress.
			if not settings.get('output.deduplicate_files'):
				# Deduplication disabled.
				return file_path #!cover
			was_new, existing_path = hashjar.add_hash(file_path) # Check if the file exists already.
			if not was_new and existing_path != file_path:
				# Quick and dirty comparison, assumes larger filesize means better quality.
				if os.path.isfile(file_path) and os.path.isfile(existing_path):
					if os.path.getsize(file_path) > os.path.getsize(existing_path):
						manifest.remove_file_hash(existing_path) #TODO: This should callback through HashJar, just to keep it centralized. Also, this should probably call *before* the file deletion, to avoid tracking nonexistant files (in event of crash between deletion and removal)
						os.remove(existing_path)
						manifest.remap_filepath(existing_path, file_path)
						return file_path
					else:
						manifest.remove_file_hash(file_path) #TODO: This should callback through HashJar, just to keep it centralized.
						os.remove(file_path)
						return existing_path
			return file_path
	# exit lock


	def load_handlers(self):
		""" Loads all the available handlers from the handler directory. """
		self.handlers = []
		for _,name,_ in pkgutil.iter_modules([os.path.dirname(handlers.__file__)]):
			fi = __import__('classes.handlers.%s' % name, fromlist=[''])
			self.handlers.append(fi)
		self.handlers.sort(key=lambda x: x.order, reverse=False)
		#print("Loaded handlers: ", ', '.join([x.tag for x in self.handlers]) )
		assert len(self.handlers)>0
#