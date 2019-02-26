import re
import sys
import threading
from static import settings
from static import stringutil as su
from processing.redditloader import RedditLoader
from processing.downloader import Downloader
import sql
from processing.wrappers import SanitizedRelFile
import colorama
import time
import multiprocessing


class RMD(threading.Thread):
	def __init__(self, source_patterns=None):
		super().__init__()
		self.daemon = False
		self.sources = source_patterns
		self.sources = self.load_sources()
		# initialize Loader
		self.loader = RedditLoader(sources=self.sources, settings_json=settings.to_json())
		self._downloaders = self._create_downloaders()

	def run(self):
		# Initialize Database
		db_file = SanitizedRelFile(base=settings.get("output.base_dir"), file_path="manifest.sqldb")
		db_file.mkdirs()
		sql.init(db_file.absolute())

		# Start Post scanner, with a Queue
		self.loader.start()
		for dl in self._downloaders:
			dl.start()

		# TODO: Remove this basic printout, and add wrapper UIs for the downloader to support Console/Web
		min_timer = multiprocessing.Event()
		while any(p.is_alive() for p in self._downloaders):
			if settings.get('threading.console_clear_screen'):
				print('\n'*10, colorama.ansi.clear_screen())
			print(time.time(), 'Alive:', [p.name for p in self._downloaders if p.is_alive()])
			for dl in self._downloaders:
				print()
				print('Downloader:', dl.name)
				print('Handler:'.rjust(20), dl.progress.get_handler())
				print('File:'.rjust(20), dl.progress.get_file())
				print('Status:'.rjust(20), dl.progress.get_status())
				if dl.progress.get_percent():
					print('Percent:'.rjust(20), '%s%%' % dl.progress.get_percent())
				else:
					print()
			if not self.loader.get_stop_event().is_set():
				self.loader.get_stop_event().wait(settings.get("threading.display_refresh_rate"))
			else:
				min_timer.wait(1)  # Minimum timeout, since the event will be set before processes close.

		# Start Downloaders, with the Queue.
		# Wait for Downloaders to finish.
		# TODO: status updating for console/UI.
		# TODO: If any Downloaders are finished, but the Loader is still hung, an ACK failed and we should alert.
		sql.close()
		print("All finished.")

	def stop(self):
		self.loader.get_stop_event().set()  # TODO: fully implement

	def is_running(self):
		pass  # TODO: implement

	def get_progress(self):
		return [d.progress for d in self._downloaders]

	def _create_downloaders(self):
		dls = []
		for i in range(settings.get('threading.concurrent_downloads')):
			tp = Downloader(
				reader=self.loader.get_reader(),
				ack_queue=self.loader.get_ack_queue(),
				settings_json=settings.to_json()
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
