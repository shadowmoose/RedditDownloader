import stringutil
import colorama
import os
import queue
from processing.handlerthread import HandlerThread
import time

class ElementProcessor:
	""" The heavy-lifting bit. Handles processing all the Elements provided to it via the generator it's created with, by finding the most appropriate Handler for each Element. """
	
	def __init__(self, reddit_loader, settings, manifest):
		""" Creates and prepares the Processor object, with the given RedditLoader to provide RedditElements. Takes a loaded Settings object to find the configured save path. """
		self.loader = reddit_loader
		self.gen = self.loader.get_elements()
		self.settings = settings
		self.manifest = manifest
		self.handlers = []
		self.threads = []
	#
	
	def run(self):
		q = queue.Queue()
		for ele in self.gen:
			q.put(ele)

		#start threads
		for i in range(5):# TODO: Setting for thread count
			ht = HandlerThread('Handler - %s' % (i+1), self.settings, self.manifest, self.loader, q)
			ht.daemon = True
			ht.start()
			self.threads.append(ht)
		try:
			while any([t.keep_running for t in self.threads]):
				out = colorama.ansi.clear_screen()
				out+=("Waiting for queue... (~%s)" % q.qsize())+"\n"
				#TODO: Display thread progress here.
				for th in self.threads:
					out+=th.name+"\n"
					out+=th.log.render()
					out+=th.handler_log.render()
					out+="\n"
				print(out)
				time.sleep(1) # TODO: Setting for refresh rate?
			#print("Completing queue...")
			#q.join()
			print("Queue finished!")
		except:
			self.stop_process()
			raise
	#


	def stop_process(self):
		""" Signal any running threads that they should exit. """
		for th in self.threads:
			th.keep_running = False