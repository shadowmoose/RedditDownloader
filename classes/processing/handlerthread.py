import threading
import queue
import os
import pkgutil
import sys

import stringutil
import processing.logger
import handlers
import hashjar


class HandlerThread(threading.Thread):
	ele_lock = threading.RLock()
	used_files = []

	def __init__(self, name, settings, manifest, loader, queue):
		threading.Thread.__init__(self)
		self.name = name
		self.log = processing.logger.Logger(2, padding=1)
		self.handler_log = processing.logger.Logger(2, padding=2)
		self.handlers = []

		self.settings = settings
		self.loader = loader
		self.manifest = manifest
		self.queue = queue
		self.load_handlers()
		self.keep_running = True


	def run(self):
		self.log.out(0, 'Starting up.')
		while self.keep_running:
			self.log.out(0, "Waiting for queue...")
			self.handler_log.clear()
			try:
				item = self.queue.get(False)
				try:
					self.process_ele(item)
				finally:
					self.queue.task_done()
			except queue.Empty:
				self.keep_running = False
				print("Exited thread %s" % self.name)
				break
		self.log.out(0,stringutil.color('Completed.', stringutil.Fore.GREEN))
		self.handler_log.clear()
		self.keep_running = False




	def process_ele(self, reddit_element):
		""" Accepts a RedditElement of Post/Comment details, then runs through the Handlers loaded from the other directory, attempting to download the url.  """
		todo = []
		self.log.out(0, 'Processing new ele...')
		self.handler_log.clear()
		with HandlerThread.ele_lock:
			self.log.out(0,
				 stringutil.out(
					 "[%s](%s): %s" % (reddit_element.type, reddit_element.subreddit, reddit_element.title),
					 False,
					 stringutil.Fore.LIGHTYELLOW_EX
				 )
			 )
			for url in reddit_element.get_urls():
				file = self.loader.url_exists(url)
				if file:
					reddit_element.add_file(url, file)
					continue
				if self.manifest:
					skip, file = self.manifest.url_completed(url)
					if skip and (file is None or os.path.exists(file)):
						reddit_element.add_file(url, file)
						if file is not None:
							hashjar.add_hash(file) # Add the existing file hash so we can deduplicate against it.
						continue
				file_info = self.build_file_info(reddit_element)# Build the file information dict using this RedditElement's information
				if file_info is None:
					reddit_element.add_file(url, False)
				else:
					todo.append({'url':url, 'info':file_info})
		#exit lock

		for el in todo:
			url = el['url']
			file_info = el['info']
			file_path = self.process_url(url, file_info)# The important bit is here, & doesn't need the Lock.
			if not self.keep_running:
				return # Kill the thread after a potentially long-running download, if the program has terminated.
			with HandlerThread.ele_lock:
				reddit_element.add_file(url, self.check_duplicates(file_path))
			# exit lock
	#


	def build_file_info(self, reddit_element):
		""" Generates a dict of file locations and element data that is passed down to every handler, so they can choose where best to save for themselves. """
		with HandlerThread.ele_lock:
			dir_pattern  = '%s/%s' % ( self.settings.save_base() , self.settings.save_subdir() )
			file_pattern = '%s/%s' % ( dir_pattern, self.settings.save_filename())

			basedir = stringutil.insert_vars(dir_pattern, reddit_element)
			basefile = stringutil.insert_vars(file_pattern, reddit_element)

			if basedir is None or basefile is None:
				#Cannot download this file, because the file path generated for it is too long
				return None

			og = basefile
			i=2
			while basefile in HandlerThread.used_files:
				#Use local list of filenames used here, since used filenames won't be updated until done otherwise.
				basefile = og+' . '+str(i)
				basefile = stringutil.normalize_file(basefile)
				i+=1
			HandlerThread.used_files.append(basefile)

			# Build an array of pre-generated possible locations & important data for handlers to have access to.
			return {
				'parent_dir'	: basedir,			# Some handlers will need to build the parent directory for their single file first. This simplifies parsing.
				'single_file'	: basefile+"%s",	# If this handler can output a single file, it will use this path.
				'multi_dir' 	: basefile+"/",		# If the handler is going to download multiple files, it will save them under this directory.
				'post_title'	: reddit_element.title,			# The title of the Reddit post.
				'post_subreddit': reddit_element.subreddit,		# The subreddit this post came from.
				'user_agent'	: self.settings.get('auth', None)['user_agent'],
			}
		# exit lock.


	def process_url(self, url, info):
		""" Accepts a URL and the array of file info generated for it by this class, and then attempts to download it using any possible handler.
			Returns whatever the handlers do, which should be a path to the file itself or the containing directory for an album.
				+Also returns False or None if no appropriate handler was found, or if the handler told us not to download anything.
		"""
		ret_val = False # Default to 'False', meaning no file was located by a handler.
		for h in self.handlers:
			self.log.out(1,stringutil.color("Checking handler: %s" % h.tag, stringutil.Fore.CYAN))
			ret = False

			# noinspection PyBroadException
			try:
				ret = h.handle(url, info, self.handler_log)
			except Exception:# There are too many possible exceptions between all handlers to catch properly.
				print(sys.exc_info()[0])
				pass

			if ret is None:
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
			Returns the filename that the file exists under.
		"""
		if not file_path:
			return file_path
		with HandlerThread.ele_lock:
			if not self.settings.get('deduplicate_files', True):
				# Deduplication disabled.
				return file_path
			was_new, existing_path = hashjar.add_hash(file_path) # Check if the file exists already.
			if not was_new:
				# Quick and dirty comparison, assumes larger filesize means better quality.
				if os.path.isfile(file_path) and os.path.isfile(existing_path):
					if os.path.getsize(file_path) > os.path.getsize(existing_path):
						os.remove(existing_path)
						for ele in self.loader.get_elements_for_file(existing_path):
							ele.remap_file(existing_path, file_path)
						return file_path
					else:
						os.remove(file_path)
						return existing_path
			return file_path
		# exit lock


	def load_handlers(self):
		""" Loads all the available handlers from the handler directory. """
		self.handlers = []
		for _,name,_ in pkgutil.iter_modules([os.path.dirname(handlers.__file__)]):
			if '_init_' in name:
				continue
			fi = __import__(name, fromlist=[''])
			self.handlers.append(fi)
		self.handlers.sort(key=lambda x: x.order, reverse=False)
		print("Loaded handlers: ", ', '.join([x.tag for x in self.handlers]) )
		assert len(self.handlers)>0
#