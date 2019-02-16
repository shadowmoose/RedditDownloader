import multiprocessing
import queue
from colorama import Fore
from static import stringutil
import static.settings as settings
from processing.queue_reader import QueueReader


class RedditLoader(multiprocessing.Process):
	def __init__(self, sources, settings_json):
		""" This is a daemon Loader class, which facilitates loading from multiple Sources,
		 	and safely popping Posts off an internal queue.

		 	Anything that creates a Reader is responsible for flagging when it should stop, using the provided Event.
		"""
		super().__init__()
		self.sources = sources
		self.settings = settings_json
		self._queue = multiprocessing.Queue(maxsize=500)
		self._open_ack = set()
		self._ack_queue = multiprocessing.Queue()
		self._stop_event = multiprocessing.Event()  # This is a shared mp.Event, set when this reader should be done.
		self._reader = QueueReader(input_queue=self._queue, stop_event=self._stop_event)
		self.daemon = True
		self.name = 'RedditElementLoader'

	def run(self):
		""" Threaded loading of elements. """
		print("Loading elements...", self.sources)
		settings.from_json(self.settings)

		# TODO: Query for all unhandled URLs, and submit them before scanning for new Posts.

		for source in self.sources:
			try:
				stringutil.print_color(Fore.GREEN, 'Downloading from Source: %s' % source.get_alias())
				for r in source.get_elements():
					r.set_source(source)
					# TODO: If New URL, Create the Post/URL objects, and submit the URL ID instead of the RedditElement.
					self._push_url(r)

				# Wait for any remaining ACKS to come in, before closing the writing pipe.
				# ...Until the Downloaders have confirmed completion of everything, more album URLS may come in.
				stringutil.print_color(Fore.GREEN, 'Waiting for acks...')
				while len(self._open_ack) > 0:
					self._handle_acks()
			except ConnectionError as ce:
				print(str(ce).upper())
				# TODO: How to best log a failure here?
		print("Finished loading.")
		self._stop_event.set()

	def count_remaining(self):
		""" Approximate the remaining elements in the queue. """
		return self._queue.qsize()

	def get_reader(self):
		return self._reader

	def get_ack(self):
		return self._ack_queue

	def get_stop_event(self):
		return self._stop_event

	def _push_url(self, url):
		# TODO: Create the Post/URL objects, and submit the URL ID instead of the RedditElement.
		self._handle_acks()  # passively process some ACKS in a non-blocking way to prevent queue bloat.
		while not self._stop_event.is_set():
			try:  # Keep trying to add this element to the queue, with a timeout to catch any stop triggers.
				self._queue.put(url, timeout=1)
				self._open_ack.add(url.id)  # Replace after testing.
				break
			except queue.Full:
				pass

	def _handle_acks(self):
		try:
			packet = self._ack_queue.get_nowait()
			if packet['cmd'] == 'ack':
				self._open_ack.remove(packet['id'])
			else:
				print('Downloader reported new Album URL IDs:', packet)
				# TODO: Take the submitted list of Album URLS, generate them in the DB, and submit them.
		except queue.Empty:
			pass
