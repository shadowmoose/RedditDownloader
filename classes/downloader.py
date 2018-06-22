import time
import datetime
import re
import sys
import threading
from colorama import Fore
from classes.static import settings
from classes.processing.elementprocessor import ElementProcessor
from processing.redditloader import RedditLoader
from classes.static import stringutil as su


class RMD(threading.Thread):
	def __init__(self, source_patterns=None, test=False):
		super().__init__()
		self.daemon = False
		self.sources = source_patterns
		self.sources = self.load_sources()
		self.test = test
		self.loader = None
		self.processor = None


	def run(self):
		_start_time = time.time()
		try:
			self.loader = RedditLoader(self.test)
			self.loader.scan(self.sources) # Starts the scanner thread.
			self.processor = ElementProcessor(self.loader)
			self.processor.run()  # hangs until processor runs out of elements.
			# Reaching this point should indicate that the loader & processor are finished.
		except Exception:
			raise
		finally:
			self.stop()
		_total_time = str( datetime.timedelta(seconds= round(time.time() - _start_time)) )
		su.print_color(Fore.GREEN, 'Found %s posts missing files - with %s new files downloaded - and %s files that cannot be found.' %
			  (self.processor.total_posts, self.processor.total_urls, self.processor.failed_urls))
		print('Finished processing in %s.' % _total_time)


	def stop(self):
		if self.loader:
			self.loader.stop()
		if self.processor:
			self.processor.stop_process()


	def is_running(self):
		return super(RMD, self).isAlive() or self.loader.isAlive() or self.processor.is_running()


	def load_sources(self): #!cover
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
					if regexp.search( str(s.get_alias()) ):
						print('Matched Source: ', s.get_alias() )
						sources.append(s)
						break
		if len(sources) == 0:
			if len(settings_sources) == 0:
				su.error('No sources were found from the settings file.')
			else:
				su.error('No sources were found from the settings file matching the supplied patterns.')
			sys.exit(20)
		return sources
