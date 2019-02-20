import multiprocessing
import sql
from static import settings
from processing.wrappers import SanitizedRelFile, AckPacket, Progress
import handlers
import uuid

# TODO: Extend this to allow direct console input by wrapping the input/output queues.


class Downloader(multiprocessing.Process):
	def __init__(self, reader, ack_queue, settings_json):
		"""
		Create a Downloader Process, which will be bound to the queue given, listening for URLs to download.
		"""
		super().__init__()
		self._reader = reader
		self._settings = settings_json
		self.progress = Progress()
		self._session = None
		self._ack_queue = ack_queue
		self.daemon = True

	def run(self):
		""" Threaded loading of elements. """
		settings.from_json(self._settings)
		db_file = SanitizedRelFile(base=settings.get("output.base_dir"), file_path="manifest.sqldb")
		db_file.mkdirs()
		sql.init(db_file.absolute())
		self._session = sql.session()
		self.progress.clear(status="Starting up...")

		for nxt_id in self._reader:
			try:
				url = self._session.query(sql.URL).filter(sql.URL.id == nxt_id).first()
				if not url:
					raise Exception("Unknown URL ID provided: (%s}" % nxt_id)  # TODO: Log this instead, after testing.

				file = url.files[0]  # Eventually it may be prudent to support multiple files per URL.
				path = SanitizedRelFile(base=settings.get("output.base_dir"), file_path=file.path)

				self.progress.set_file(path.relative())
				self.progress.set_status("Attempting to Handle URL...")

				task = handlers.HandlerTask(url=url.address, file_obj=path)
				resp = handlers.handle(task, self.progress)

				if resp.album_urls:
					if url.album_id:
						resp.album_urls = []  # Ignore nested Albums to avoid recursion.
					else:
						url.album_id = str(uuid.uuid4())
				else:
					resp.album_urls = []

				url.downloaded = resp.success
				url.failed = not resp.success
				url.failure_reason = resp.failure_reason
				url.last_handler = resp.handler

				if resp.rel_file:
					file.downloaded = True
					file.path = resp.rel_file.relative()
					file.hash = None

				self._session.commit()
				# TODO: Hash file and deduplicate.

				# Once *all* processing is completed on this URL, the Downloader needs to ACK it.
				# If any additional Album URLS were located, they should be sent before the ACK.
				self._ack_queue.put(AckPacket(
					url_id=nxt_id,
					post_id=url.post_id,
					album_id=url.album_id,
					extra_urls=resp.album_urls
				))
				self.progress.clear(status="Waiting for Post...")
			except Exception:
				self._ack_queue.put(AckPacket(
					url_id=nxt_id,
					post_id=None,
					album_id=None,
					extra_urls=[]
				))
				raise  # TODO: Error handling here.

		self._session = sql.session()
		print("Finished reading.")
		self.progress.clear("Finished.")
