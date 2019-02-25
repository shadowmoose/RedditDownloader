from processing.wrappers.rel_file import RelFile, SanitizedRelFile
from processing.wrappers.queue_reader import QueueReader
from multiprocessing import Manager


class AckPacket:
	def __init__(self, url_id, extra_urls):
		self.url_id = url_id
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

	def set_percent(self, prog):
		self._ns.percent = str(prog).strip() if prog is not None else None

	def get_percent(self):
		return self._ns.percent

	def set_status(self, status):
		self._ns.status = str(status)

	def get_status(self):
		return self._ns.status

	def set_handler(self, handler):
		self._ns.handler = str(handler)

	def get_handler(self):
		return self._ns.handler

	def set_file(self, file_name):
		self._ns.file_name = str(file_name)

	def get_file(self):
		return str(self._ns.file_name)

	def clear(self, status=""):
		""" Reset this Progress to the default values. Optionally accepts `status` as a convenience. """
		self._ns.percent = None
		self._ns.status = status
		self._ns.handler = None
		self._ns.file_name = None
