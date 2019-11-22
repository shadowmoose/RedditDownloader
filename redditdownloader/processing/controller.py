import re
import sys
import threading
import sql
from static import settings
from static import stringutil as su
from processing.redditloader import RedditLoader
from processing.downloader import Downloader
from processing.post_processing import Deduplicator
from processing.wrappers import ProgressManifest
from multiprocessing import RLock


class RMDController(threading.Thread):
	def __init__(self, source_patterns=None):
		super().__init__()
		sql.init_from_settings()  # Make sure the database is built & migrated before starting threads.
		sql.close()
		self.daemon = False
		self.sources = source_patterns
		self.sources = self.load_sources()
		self.db_lock = RLock()
		# initialize Loader
		self.loader = RedditLoader(sources=self.sources, settings_json=settings.to_json(), db_lock=self.db_lock)
		self.deduplicator = Deduplicator(
			settings_json=settings.to_json(),
			stop_event=self.loader.get_stop_event(),
			db_lock=self.db_lock
		)
		self._downloaders = self._create_downloaders()
		self._all_processes = [self.loader, *self._downloaders]
		if settings.get('processing.deduplicate_files'):
			self._all_processes.append(self.deduplicator)

	def run(self):
		for dl in self._all_processes:
			dl.start()
		[t.join() for t in self._all_processes]

	def stop(self):
		self.loader.get_stop_event().set()
		for d in self._downloaders:
			d.terminate()
		self.loader.terminate()

	def is_running(self):
		return any(d.is_alive() for d in self._all_processes)

	def get_progress(self):
		return ProgressManifest(
			downloaders=[d.progress for d in self._downloaders],
			loader=self.loader.progress,
			deduplication=self.deduplicator.progress,
			running=self.is_alive()
		)

	def wait_refresh_rate(self):
		"""
		Waits for the "refresh delay" configured in the settings, or exits early if processing finished before then.
		:return: True if the delay was fully awaited, or False if processing has completed.
		"""
		if not self.loader.get_stop_event().is_set():
			self.loader.get_stop_event().wait(settings.get("threading.display_refresh_rate"))
			return True
		return False

	def _create_downloaders(self):
		dls = []
		for i in range(settings.get('threading.concurrent_downloads')):
			tp = Downloader(
				reader=self.loader.get_reader(),
				ack_queue=self.loader.get_ack_queue(),
				settings_json=settings.to_json(),
				db_lock = self.db_lock
			)
			dls.append(tp)
		return dls

	def load_sources(self):  # !cover
		sources = []
		settings_sources = settings.get_sources()
		if self.sources is None:
			for s in settings_sources:
				print('Loaded Source: ', s.get_alias())
				sources.append(s)
		else:
			for so in self.sources:
				regexp = re.compile(str(so), re.IGNORECASE)
				for s in settings_sources:
					if regexp.search(str(s.get_alias())):
						print('Matched Source: ', s.get_alias())
						sources.append(s)
						break
		if len(sources) == 0:
			if len(settings_sources) == 0:
				su.error('No sources were found from the settings file.')
			else:
				su.error('No sources were found from the settings file matching the supplied patterns.')
			sys.exit(20)
		return sources
