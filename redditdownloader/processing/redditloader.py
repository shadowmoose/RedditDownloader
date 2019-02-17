import multiprocessing
import queue
from colorama import Fore
from static import stringutil
import static.settings as settings
from processing.queue_reader import QueueReader
from processing.rel_file import SanitizedRelFile
import sql
from processing import name_generator

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
						self._session.add(post)
					urls = self._create_new_urls(r, post)
					for u in urls:
						self._create_url_files(u)
						self._push_url(u.id)
					self._session.commit()

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

	def _create_new_urls(self, reddit_element, post):
		"""
		Creates and Commits all the *new* URLS in the given RedditElement,
		then returns a list of the new URLs.
		"""
		urls = []
		for u in reddit_element.get_urls():
			if self._session.query(sql.URL.id).filter(sql.URL.address == u).first():
				print("Skipping url.")
				# These URLS can be skipped, because they are top-level "non-album-file" urls.
				# Album URLs will be resubmitted submitted in a differet method.
				continue
			url = sql.URL.make_url(u, post, None, 0)
			urls.append(url)
		self._session.add_all(urls)
		self._session.commit()  # After commiting, the URL generated IDs will be filled in.
		return urls

	def _create_url_files(self, url):
		"""
		Builds the desired sql.File object for the given sql.URL Object.
		Automatically adds the File object to the URL.
		"""
		filename = name_generator.choose_file_name(url, self._session)
		file = sql.File(
			path=filename,
			url_id=url.id
		)
		url.files.append(file)
		self._session.commit()

	def count_remaining(self):
		""" Approximate the remaining elements in the queue. """
		return self._queue.qsize()

	def get_reader(self):
		return self._reader

	def get_ack(self):
		return self._ack_queue

	def get_stop_event(self):
		return self._stop_event

	def _push_url(self, url_id):
		self._handle_acks()  # passively process some ACKS in a non-blocking way to prevent queue bloat.
		while not self._stop_event.is_set():
			try:  # Keep trying to add this element to the queue, with a timeout to catch any stop triggers.
				self._queue.put(url_id, timeout=1)
				self._open_ack.add(url_id)  # Replace after testing.
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
