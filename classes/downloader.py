import os
import time
import datetime
import re
import sys
from colorama import Fore
from classes.util import settings
from classes.processing.elementprocessor import ElementProcessor
from classes.reddit.redditloader import RedditLoader
import classes.util.manifest as manifest
import classes.reddit.praw_wrapper as reddit
from classes.util import stringutil as su


class RMD(object):
	def __init__(self, source_patterns=None, test=False):
		if not os.path.isdir(settings.save_base()):
			os.makedirs(os.path.abspath(settings.save_base()) )
		os.chdir(settings.save_base()) # Hop into base dir, so all file work can be relative.
		self.sources = source_patterns
		self.test = test
		self.sources = self.load_sources()
		self.reddit = None
		self.processor = None


	def connect(self):
		# Authenticate and prepare to scan:
		reddit.init(client_id=settings.get('auth.client_id'), client_secret=settings.get('auth.client_secret'),
					password=settings.get('auth.password'), user_agent=settings.get('auth.user_agent'), username=settings.get('auth.username'))
		reddit.login()
		manifest.create('manifest.sqldb')
		manifest.check_legacy(settings.save_base())  # Convert away from legacy Manifest.


	def run(self):
		_start_time = time.time()
		try:
			self.reddit = RedditLoader(self.test)
			self.reddit.scan(self.sources) # Starts the scanner thread.
			self.processor = ElementProcessor(self.reddit)
			self.processor.run()
		except KeyboardInterrupt:
			print("Interrupted by User.")
			self.stop()
		_total_time = str( datetime.timedelta(seconds= round(time.time() - _start_time)) )
		su.print_color(Fore.GREEN, 'Found %s posts missing files - with %s new files downloaded - and %s files that cannot be found.' %
			  (self.processor.total_posts, self.processor.total_urls, self.processor.failed_urls))
		print('Finished processing in %s.' % _total_time)


	def stop(self):
		if self.reddit:
			self.reddit.stop()
		if self.processor:
			self.processor.stop_process()


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
