import re
import sys
import threading
from static import settings
from static import stringutil as su
from processing.redditloader import RedditLoader
from processing.test_process import TestProcess

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
		self.processor = None
		self._total_time = 0

	def run(self):
		# Start Post scanner, with a Queue
		self.loader.start()

		tests = []
		for i in range(5):
			tp = TestProcess(reader=self.loader.get_reader(), ack=self.loader.get_ack())
			tests.append(tp)
			tp.start()

		for t in tests:
			t.join()

		# Start Downloaders, with the Queue.
		# Wait for Downloaders to finish.
		# TODO: status updating for console/UI.
		# TODO: If all the Downloaders are finished, but the Loader is still hung, an ACK failed and we should alert.
		print("All finished.")

	def stop(self):
		self.loader.get_stop_event().set()  # TODO: fully implement

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
