import multiprocessing
import sql
from static import settings
from processing.wrappers import SanitizedRelFile, AckPacket, DownloaderProgress
from processing import handlers
import uuid
import traceback


class Downloader(multiprocessing.Process):
	def __init__(self, reader, ack_queue, settings_json):
		"""
		Create a Downloader Process, which will be bound to the queue given, listening for URLs to download.
		"""
		super().__init__()
		self._reader = reader
		self._settings = settings_json
		self.progress = DownloaderProgress()
		self._session = None
		self._ack_queue = ack_queue
		self.daemon = True

	def run(self):
		""" Threaded loading of elements. """
		settings.from_json(self._settings)
		sql.init_from_settings()
		self._session = sql.session()
		self.progress.clear(status="Starting up...", running=True)
		failed = False

		for nxt_id in self._reader:
			try:
				url = self._session.query(sql.URL).filter(sql.URL.id == nxt_id).first()
				if not url:
					raise Exception("Unknown URL ID provided: (%s}" % nxt_id)

				file = url.file
				path = SanitizedRelFile(base=settings.get("output.base_dir"), file_path=file.path)

				self.progress.set_file(path.relative())
				self.progress.set_status("Attempting to Handle URL...")
				self.progress.set_running(True)

				task = handlers.HandlerTask(url=url.address, file_obj=path)
				resp = handlers.handle(task, self.progress)

				is_album_parent = False

				if resp.album_urls:
					if url.album_id:
						resp.album_urls = []  # Ignore nested Albums to avoid recursion.
					else:
						url.album_id = str(uuid.uuid4())
						is_album_parent = True
				else:
					resp.album_urls = []

				url.failed = not resp.success
				url.failure_reason = resp.failure_reason
				url.last_handler = resp.handler
				url.album_is_parent = is_album_parent

				if resp.rel_file:
					file.downloaded = True
					file.path = resp.rel_file.relative()
					file.hash = None

				self._session.commit()

				# Once *all* processing is completed on this URL, the Downloader needs to ACK it.
				# If any additional Album URLS were located, they should be sent before the ACK.
				self._ack_queue.put(AckPacket(
					url_id=nxt_id,
					extra_urls=resp.album_urls
				))
				self.progress.clear(status="Waiting for URL...")
			except Exception as ex:
				failed = str(ex)
				self._ack_queue.put(AckPacket(
					url_id=nxt_id,
					extra_urls=[]
				))
				print(ex)
				traceback.print_exc()
				break

		sql.close()
		self.progress.clear("Finished." if not failed else "Exited with error: %s" % failed, running=False)
