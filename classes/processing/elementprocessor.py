import colorama
import time
import shutil
from classes.processing.handlerthread import HandlerThread
from classes.util import stringutil
from classes.util import settings


class ElementProcessor:
	""" The heavy-lifting bit. Handles processing all the Elements provided to it via the generator it's created with, by finding the most appropriate Handler for each Element. """
	
	def __init__(self, reddit_loader):
		""" Creates and prepares the Processor object, with the given RedditLoader to provide RedditElements. Takes a loaded Settings object to find the configured save path. """
		self._loader = reddit_loader
		self.handlers = []
		self.threads = []

		self.total_urls = 0
		self.total_posts = 0
		self.failed_urls = 0


	def run(self):
		max_threads = settings.get('threading.max_handler_threads')
		HandlerThread.reset()
		#start threads
		for i in range(max_threads):
			ht = HandlerThread('Handler - %s' % (i+1), self._loader)
			ht.daemon = True
			ht.start()
			self.threads.append(ht)
		try:
			clear = settings.get('threading.display_clear_screen')
			refresh_rate = max(0.1, settings.get('threading.display_refresh_rate'))

			while any([t.keep_running for t in self.threads]):
				self.redraw(clear)
				# Sleep...
				if refresh_rate > 5: #!cover
					steps = max(1, int(refresh_rate/5))
					for t in range(steps):
						# Break custom output delay down, so we can exit early if finished.
						time.sleep(refresh_rate/steps)
						if not any([t.keep_running for t in self.threads]):
							break
					time.sleep(refresh_rate % 5) # Add any extra time on there, to be precise.
				else:
					time.sleep(refresh_rate)
				self.total_posts = sum(th.total_new_posts for th in self.threads)
				self.total_urls = sum(th.total_new_urls for th in self.threads)
				self.failed_urls = sum(th.total_failed_urls for th in self.threads)
			self.redraw(clear)
			print("\r\nQueue finished! (Total Processed: %s)" % self._loader.count_total())
		except:
			self.stop_process()
			raise
	#


	def redraw(self, clear, depth=0):
		""" Redraws the current Thread process.
		:param clear: If the screen should be cleared before redrawing.
				(Ignored automatically if not supported/possible.)
		:param depth: The times this function has recursively called. Max limit of one.
		:return:
		"""
		max_threads = len(self.threads)
		dim = shutil.get_terminal_size((0,0))
		width = dim.columns
		height = dim.lines
		out = ''

		lines_per = max(2, int((height - 2)/(max_threads+1)) )
		if lines_per < 3: # 4 lines = thread name+two levels of info + newline.
			clear = False

		if clear:
			out = colorama.ansi.clear_screen()

		if not clear:
			print('\n\n\n\n')

		out+= stringutil.color("Processing Posts: (~%s in queue, %s %s)" % (
			self._loader.count_remaining(),
			self._loader.count_total(),
			'found so far' if self._loader.is_running() else 'Total'
		), colorama.Fore.CYAN )
		out+= "\n"
		for th in self.threads:
			if th.keep_running:
				head_color = stringutil.Fore.GREEN
			else:
				head_color = stringutil.Fore.LIGHTYELLOW_EX
			out+= stringutil.color(th.name, head_color) + "\n"
			out+=th.log.render(limit=2, max_width=width)
			out+=th.handler_log.render(limit=lines_per-2, max_width=width)
		# noinspection PyBroadException
		try:
			print(out.rstrip(), end='')
		except:
			if depth <= 1:
				self.redraw(False, depth+1)
				return
			else:
				raise
		if not clear:
			print('\n\n')


	def stop_process(self):
		""" Signal any running threads that they should exit. Non-blocking. """
		for th in self.threads: #!cover
			th.keep_running = False
