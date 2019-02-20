from processing.wrappers.rel_file import RelFile, SanitizedRelFile
from processing.wrappers.queue_reader import QueueReader
from multiprocessing import Manager


class AckPacket:
	def __init__(self, url_id, post_id, album_id, extra_urls):
		self.url_id = url_id
		self.post_id = post_id
		self.album_id = album_id
		self.extra_urls = extra_urls


class Progress:
	"""
	Progress is a wrapper for multiprocessing's Manager class.
	It is capable of syncing status across multiple Processes.
	"""
	_manager = None

	def __init__(self):
		if not Progress._manager:
			Progress._manager = Manager()
			print("Created NamespaceManager.")
		self._ns = Progress._manager.Namespace()
		self.clear()  # Initialize the progress variables as their defaults.

	def set_progress(self, prog):
		self._ns.progress = str(prog) if prog is not None else None

	def get_progress(self):
		return self._ns.progress

	def set_status(self, status):
		self._ns.status = str(status)

	def get_status(self):
		return self._ns.status

	def set_handler(self, handler):
		self._ns.handler = str(handler)

	def get_handler(self):
		return self._ns.handler

	def clear(self, status=""):
		""" Reset this Progress to the default values. Optionally accepts `status` as a convenience. """
		self._ns.progress = None
		self._ns.status = status
		self._ns.handler = None
