import multiprocessing
import queue
from static import stringutil
from static import settings
from processing import name_generator
from processing.wrappers import QueueReader, SanitizedRelFile, LoaderProgress
import sql


class RedditLoader(multiprocessing.Process):
	def __init__(self, sources, settings_json):
		""" This is a daemon Loader class, which facilitates loading from multiple Sources
		 	and safely submitting their Posts to an internal queue.
		"""
		super().__init__()
		self.sources = sources
		self.settings = settings_json
		self._queue = multiprocessing.Queue(maxsize=2500)
		self._open_ack = set()
		self._ack_queue = multiprocessing.Queue()
		self._stop_event = multiprocessing.Event()  # This is a shared mp.Event, set when this reader should be done.
		self._reader = QueueReader(input_queue=self._queue, stop_event=self._stop_event)
		self._session = None
		self.progress = LoaderProgress()
		self.daemon = True
		self.name = 'RedditElementLoader'

	def run(self):
		""" Threaded loading of elements. """
		settings.from_json(self.settings)
		sql.init_from_settings()
		self._session = sql.session()

		# Query for all unhandled URLs, and submit them before scanning for new Posts.
		unfinished = self._session\
			.query(sql.URL)\
			.filter((sql.URL.processed == False) | (sql.URL.failed == True))\
			.all()
		self._push_url_list(unfinished)

		self._scan_sources()

		self.progress.set_scanning(False)
		# Wait for any remaining ACKS to come in, before closing the writing pipe.
		# ...Until the Downloaders have confirmed completion of everything, more album URLS may come in.
		while len(self._open_ack) > 0 and not self._stop_event.is_set():
			self._handle_acks(timeout=0.5)
		print("Finished loading.")
		sql.close()
		self._stop_event.set()

	def _scan_sources(self):
		for source in self.sources:
			try:
				self.progress.set_source(source.get_alias())
				for r in source.get_elements():
					if self._stop_event.is_set():
						return
					r.set_source(source)

					# Create the SQL objects, then submit them to the queue.
					post = self._session.query(sql.Post).filter(sql.Post.reddit_id == r.id).first()
					if not post:
						post = sql.Post.convert_element_to_post(r)

					urls = self._create_element_urls(r, post)
					for u in urls:
						self._create_url_file(u, post=post)
					self._session.add(post)
					self._push_url_list(urls)
			except ConnectionError as ce:
				print(str(ce).upper())
			# TODO: Log failure.

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

	def _create_album_urls(self, urls, post, album_key):
		""" Generates URL objects for Album URLs. """
		if not post:
			raise ValueError("The given Post does not exist - cannot generate Album URL: %s" % post)
		new_urls = []
		for idx, u in enumerate(urls):
			url = sql.URL.make_url(address=u, post=post, album_key=album_key, album_order=idx+1)
			new_urls.append(url)
			self._session.add(url)
			post.urls.append(url)
		return new_urls

	def _create_url_file(self, url, post, album_size=1):
		"""
		Builds the desired sql.File object for the given sql.URL Object.
		Automatically adds the File object to the URL.
		"""
		filename = name_generator.choose_file_name(url=url, post=post, session=self._session, album_size=album_size)
		file = sql.File(
			path=filename
		)
		self._session.add(file)
		url.file = file

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
		self._safe_commit()
		for u in url_list:
			self._push_url(u.id, handle_acks=handle_acks)

	def _safe_commit(self):
		""" Commit and catch any exceptions, usually raised if the session is not dirty. """
		try:
			self._session.commit()  # After commiting, the URL generated IDs will be filled in.
		except Exception as e:
			stringutil.error("RedditLoader: Error persisting session: %s" % e)
			pass

	def _push_url(self, url_id, handle_acks=True):
		if handle_acks:
			self._handle_acks()  # passively process some ACKS in a non-blocking way to prevent queue bloat.
		self.progress.increment_found()
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
		"""
		self.progress.set_queue_size(len(self._open_ack))
		try:
			packet = self._ack_queue.get(block=True, timeout=timeout)
			url = self._session.query(sql.URL).filter(sql.URL.id == packet.url_id).first()
			if packet.extra_urls:
				urls = self._create_album_urls(packet.extra_urls, url.post, url.album_id)
				for u in urls:
					self._create_url_file(u, post=url.post, album_size=len(urls))
				url.processed = True  # When the new URLs are committed, also prevent this URL from being reprocessed.
				self._push_url_list(urls, handle_acks=False)
			else:
				url.processed = True
				self._safe_commit()
			self._open_ack.remove(packet.url_id)
		except queue.Empty:
			pass
