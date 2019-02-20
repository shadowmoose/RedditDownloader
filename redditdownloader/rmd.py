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

'''
	TODO: Probably need a special class for generating file location data.
	It should accept a Post element from the DB, a URL, and if the URL is part of an Album,
	It will output a File Path, which the Downloaders will be responsible to saving to.
	
	If the Downloaders find an Album URL, they could just use the same class to generate the File Path,
	save the path to the DB, then report back the new ID so it can be queued.
'''


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
		while any(p.is_alive() for p in self._downloaders):
			if settings.get('threading.display_clear_screen'):
				print('\n'*10, colorama.ansi.clear_screen())
			for dl in self._downloaders:
				print()
				print('Downloader:', dl.name)
				print('\tHandler:', dl.progress.get_handler())
				print('\tFile:', dl.progress.get_file())
				print('\tStatus:', dl.progress.get_status())
				if dl.progress.get_percent():
					print('\tPercent:', '%s%%' % dl.progress.get_percent())
				else:
					print()
			self.loader.get_stop_event().wait(settings.get("threading.display_refresh_rate"))

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
		for i in range(settings.get('threading.max_handler_threads')):
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
