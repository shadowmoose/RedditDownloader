import multiprocessing
import sql
from static import settings
from processing.wrappers.rel_file import SanitizedRelFile
import handlers
import uuid

# TODO: Extend this to allow direct console input by wrapping the input/output queues.


class AckPacket:
	def __init__(self, url_id, post_id, album_id, extra_urls):
		self.url_id = url_id
		self.post_id = post_id
		self.album_id = album_id
		self.extra_urls = extra_urls


class TestProcess(multiprocessing.Process):
	def __init__(self, reader, ack_queue, settings_json):
		super().__init__()
		self.reader = reader
		self.settings = settings_json
		self._session = None
		self.ack_queue = ack_queue
		self.daemon = True

	def run(self):
		""" Threaded loading of elements. """
		print("Testing QueueReader...")
		settings.from_json(self.settings)
		db_file = SanitizedRelFile(base=settings.get("output.base_dir"), file_path="manifest.sqldb")
		db_file.mkdirs()
		sql.init(db_file.absolute())
		self._session = sql.session()

		for nxt_id in self.reader:
			url = self._session.query(sql.URL).filter(sql.URL.id == nxt_id).first()
			if not url:
				raise Exception("Unknown URL ID provided: (%s}" % nxt_id)  # TODO: Log this instead, after testing.

			file = url.files[0]  # Eventually it may be prudent to support multiple files per URL.
			path = SanitizedRelFile(base=settings.get("output.base_dir"), file_path=file.path)
			print("\t+URL Read:", url.address, '=>', path.absolute(), '[%s]' % multiprocessing.current_process().name)

			task = handlers.HandlerTask(url=url.address, file_obj=path)
			resp = handlers.handle(task)

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
				file.hash = None  # TODO: Hash file and deduplicate.

			self._session.commit()

			# Once *all* processing is completed on this URL, the Downloader needs to ACK it.
			# If any additional Album URLS were located, they should be sent before the ACK.
			self.ack_queue.put(AckPacket(
				url_id=nxt_id,
				post_id=url.post_id,
				album_id=url.album_id,
				extra_urls=resp.album_urls
			))  # TODO: Ack packet, which can carry any new URLS and status.

		# Start Downloaders, with the Queue.
		# Wait for Downloaders to finish.
		print("Finished reading.")
