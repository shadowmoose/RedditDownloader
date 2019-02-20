import multiprocessing
import queue
import time
from colorama import Fore
from static import stringutil
from static import settings
from processing import name_generator
from processing.wrappers import QueueReader, SanitizedRelFile
import sql


class RedditLoader(multiprocessing.Process):
	def __init__(self, sources, settings_json):
		""" This is a daemon Loader class, which facilitates loading from multiple Sources
		 	and safely submitting their Posts to an internal queue.
		"""
		super().__init__()
		self.sources = sources
		self.settings = settings_json
		self._queue = multiprocessing.Queue(maxsize=500)
		self._open_ack = set()
		self._ack_queue = multiprocessing.Queue()
		self._stop_event = multiprocessing.Event()  # This is a shared mp.Event, set when this reader should be done.
		self._reader = QueueReader(input_queue=self._queue, stop_event=self._stop_event)
		self._session = None
		self.daemon = True
		self.name = 'RedditElementLoader'

	def run(self):
		""" Threaded loading of elements. """
		print("Loading elements...", self.sources)
		settings.from_json(self.settings)
		db_file = SanitizedRelFile(base=settings.get("output.base_dir"), file_path="manifest.sqldb")
		db_file.mkdirs()
		sql.init(db_file.absolute())
		self._session = sql.session()

		# TODO: Query for all unhandled URLs, and submit them before scanning for new Posts.

		for source in self.sources:
			try:
				stringutil.print_color(Fore.GREEN, 'Downloading from Source: %s' % source.get_alias())
				for r in source.get_elements():
					r.set_source(source)

					# Create the SQL objects, then submit them to the queue.
					post = self._session.query(sql.Post).filter(sql.Post.reddit_id == r.id).first()
					if not post:
						post = sql.Post.convert_element_to_post(r)

					urls = self._create_element_urls(r, post)
					for u in urls:
						self._create_url_files(u, post=post)
					self._session.add(post)
					self._push_url_list(urls)
				# Wait for any remaining ACKS to come in, before closing the writing pipe.
				# ...Until the Downloaders have confirmed completion of everything, more album URLS may come in.
				stringutil.print_color(Fore.GREEN, 'Waiting for acks...')
				lt = time.time()
				while len(self._open_ack) > 0 and not self._stop_event.is_set():
					if time.time() - lt >= 10:  # TODO: Remove this debugging.
						lt = time.time()
						print("QUEUE [%s], AWAITING %s ACKS, {%s}" %
							  (self._queue.qsize(), len(self._open_ack), self._open_ack))
					self._handle_acks(timeout=0.5)
			except ConnectionError as ce:
				print(str(ce).upper())
				# TODO: How to best log a failure here?
		print("Finished loading.")
		sql.close()
		self._stop_event.set()

	def _create_element_urls(self, reddit_element, post):
		"""
		Creates all the *new* URLS in the given RedditElement,
		then returns a list of the new URLs.
		"""
		urls = []
		for u in reddit_element.get_urls():
			if self._session.query(sql.URL.id).filter(sql.URL.address == u).first():
				# These URLS can be skipped, because they are top-level "non-album-file" urls.
				# Album URLs will be resubmitted submitted in a differet method.
				continue
			url = sql.URL.make_url(address=u, post=post, album_key=None, album_order=0)
			urls.append(url)
			self._session.add(url)
			post.urls.append(url)
		return urls

	def _create_album_urls(self, urls, post_id, album_key):
		""" Generates URL objects for Album URLs. """
		post = self._session.query(sql.Post).filter(sql.Post.reddit_id == post_id).first()
		if not post:
			raise ValueError("The given Post ID does not exist - cannot generate Album URL: %s" % post_id)
		new_urls = []
		for idx, u in enumerate(urls):
			url = sql.URL.make_url(address=u, post=post, album_key=album_key, album_order=idx+1)
			new_urls.append(url)
			self._session.add(url)
			post.urls.append(url)
		return new_urls, post

	def _create_url_files(self, url, post, album_size=1):
		"""
		Builds the desired sql.File object for the given sql.URL Object.
		Automatically adds the File object to the URL.
		"""
		filename = name_generator.choose_file_name(url=url, post=post, session=self._session, album_size=album_size)
		file = sql.File(
			path=filename,
			url_id=url.id
		)
		self._session.add(file)
		url.files.append(file)

	def count_remaining(self):
		""" Approximate the remaining elements in the queue. """
		return self._queue.qsize()

	def get_reader(self):
		return self._reader

	def get_ack_queue(self):
		return self._ack_queue

	def get_stop_event(self):
		return self._stop_event

	def _push_url_list(self, url_list, handle_acks=True):
		"""
		Commits the session, then submits the list of URLs to the Download Queue.
		:param url_list:
		:param handle_acks:
		:return:
		"""
		# noinspection PyBroadException
		try:
			self._session.commit()  # After commiting, the URL generated IDs will be filled in.
		except Exception as e:
			stringutil.error("RedditLoader: Error persisting session: %s" % e)
			pass
		for u in url_list:
			self._push_url(u.id, handle_acks=handle_acks)

	def _push_url(self, url_id, handle_acks=True):
		if handle_acks:
			self._handle_acks()  # passively process some ACKS in a non-blocking way to prevent queue bloat.
		while not self._stop_event.is_set():
			try:  # Keep trying to add this element to the queue, with a timeout to catch any stop triggers.
				self._queue.put(url_id, timeout=1)
				self._open_ack.add(url_id)  # Replace after testing.
				break
			except queue.Full:
				pass

	def _handle_acks(self, timeout=0):
		"""
		Process an Ack Packet in the queue, if there are any.
		If not, this method will return without blocking - unless `timeout` is set.
		:return:
		"""
		try:
			packet = self._ack_queue.get(block=True, timeout=timeout)
			if packet.extra_urls:
				urls, post = self._create_album_urls(packet.extra_urls, packet.post_id, packet.album_id)
				for u in urls:
					self._create_url_files(u, post=post, album_size=len(urls))
				self._push_url_list(urls, handle_acks=False)
			self._open_ack.remove(packet.url_id)
		except queue.Empty:
			pass
