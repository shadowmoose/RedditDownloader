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
		self.load_handlers()
	#
	
	def load_handlers(self):
		""" Loads all the available handlers from the handler directory. """
		self.handlers = []
		for mod in os.listdir('classes/handlers'):
			if mod == '__init__.py' or mod[-3:] != '.py':
				continue
			lib = __import__(mod[:-3], locals(), globals())
			self.handlers.append(lib)
		#
		self.handlers.sort(key=lambda x: x.order, reverse=False)
		print("Loaded handlers: ", ', '.join([x.tag for x in self.handlers]) )
		assert len(self.handlers)>0
	#
	
	def run(self):
		q = queue.Queue()
		for ele in self.gen:
			q.put(ele)

		threads = []
		#start threads
		for i in range(5):# TODO: Setting for thread count
			ht = HandlerThread('Handler - %s' % (i+1), self.settings, self.manifest, self.loader, q)
			ht.daemon = True
			ht.start()
			threads.append(ht)

		while not q.empty():
			out = colorama.ansi.clear_screen()
			out+=("Waiting for queue... (~%s)" % q.qsize())+"\n"
			#TODO: Display thread progress here.
			for th in threads:
				out+=th.name+"\n"
				out+=th.log.render()
				out+=th.handler_log.render()
				out+="\n"
			print(out)
			time.sleep(1) # TODO: Setting for refresh rate?
		print("Completing queue")
		q.join()
		print("Queue finished!")
	#

	# TODO: Split out the below code into more clean functional logic, and move to Thread object.
