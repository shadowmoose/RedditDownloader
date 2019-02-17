import multiprocessing


class TestProcess(multiprocessing.Process):
	def __init__(self, reader, ack):
		super().__init__()
		self.reader = reader
		self.ack_queue = ack
		self.daemon = True

	def run(self):
		""" Threaded loading of elements. """
		print("Testing QueueReader...")
		self.ack_queue.put({'cmd': 'url', 'ids': ['fake1', 'fake2']})
		while True:
			nxt = self.reader.next()
			if nxt is None:
				break  # None means that the Loader has closed the Queue.

			print("\t+Post Read:", nxt, '[%s]' % multiprocessing.current_process().name)  # Mock "handling" for testing.

			# Once *all* processing is completed on this URL, the Downloader needs to ACK it.
			# If any additional Album URLS were located, they should be sent before the ACK.
			self.ack_queue.put({'cmd': 'ack', 'id': nxt})

		# Start Downloaders, with the Queue.
		# Wait for Downloaders to finish.
		print("Finished reading.")
