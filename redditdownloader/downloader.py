import re
import sys
import threading
from static import settings
from static import stringutil as su


class RMD(threading.Thread):
	def __init__(self, source_patterns=None, test=False):
		super().__init__()
		self.daemon = True
		self.sources = source_patterns
		self.sources = self.load_sources()
		self.test = test
		self.loader = None
		self.processor = None
		self._total_time = 0

	def run(self):
		# Start Post scanner, with a Queue
		# Start Downloaders, with the Queue.
		# Wait for Downloaders to finish.
		print("RMD Ran.")  # TODO: implement

	def stop(self):
		pass  # TODO: implement

	def is_running(self):
		pass  # TODO: implement

	def get_progress(self):
		pass  # TODO: implement

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
