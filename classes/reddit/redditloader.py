from colorama import Fore
import queue
import threading
from classes.util import stringutil

class RedditLoader(threading.Thread):
	def __init__(self, testing=False):
		""" Initializes a connector object to the given Reddit account, which instantly attempts to login.
			The script will hang on creating this connection, until the user is signed in.
		"""
		threading.Thread.__init__(self)
		self.sources = []
		self._testing_cache = None if not testing else []
		self._c_lock = threading.Lock()
		self._total_count = 0
		self._queue = queue.Queue(maxsize= 1000)
		self._keep_running = False
		self.daemon = True
		self.name = 'RedditElementLoader'

	
	def run(self):
		""" Threaded loading of elements. """
		self._keep_running = True
		if self._testing_cache is not None:
			self._testing_cache = []

		for source in self.sources:
			stringutil.print_color(Fore.GREEN, 'Downloading from Source: %s' % source.get_alias())
			for r in source.get_elements():
				if not self._keep_running:
					return
				r.set_source(source)
				while self._keep_running:
					try:  # Keep trying to add this element to the queue, with a timeout to catch any stop triggers.
						self._queue.put(r, timeout=1)
						break
					except queue.Full:
						pass
				# Extra tracking stuff below:
				with self._c_lock:
					self._total_count+= 1
				if self._testing_cache is not None:
					self._testing_cache.append(r)
		#print("Element loading complete.\n")
		self._keep_running = False


	def scan(self, sources):
		""" Grab all RedditElements from all the supplied Sources """
		self.sources = sources
		self.start()


	def stop(self):
		self._keep_running = False


	def is_running(self):
		""" Check if this Loader is still running. """
		return self.isAlive()


	def count_remaining(self):
		""" Approximate the remaining elements in the queue. """
		return self._queue.qsize()


	def count_total(self):
		""" Total amount of posts loaded. """
		with self._c_lock: # I can't believe I implemented a lock for a counter. Safety first, I guess...
			return self._total_count


	def next_ele(self):
		""" Gets the next element in the list. Returns Null on timeout, or raises Empty when finished. """
		try:
			ret = self._queue.get(block = True, timeout=0.5)
			self._queue.task_done()
			return ret
		except queue.Empty:
			if not self.is_running():
				raise
			else:
				return None


	def get_elements(self):
		""" If testing was enabled, returns the cache of all loaded RedditElements. """
		return self._testing_cache
