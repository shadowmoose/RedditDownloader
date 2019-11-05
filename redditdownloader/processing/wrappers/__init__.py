import json
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

	This class specifically uses getters and setters, in order to avoid improperly mutating shared data.
	"""
	_manager = None

	def __init__(self):
		if not Progress._manager:
			Progress._manager = Manager()
		self._ns = Progress._manager.dict()
		self.clear()  # Initialize the progress variables as their defaults.

	def clear(self):
		pass


class DownloaderProgress(Progress):
	def __init__(self):
		super().__init__()

	def set_percent(self, prog):
		self._ns['percent'] = str(prog).strip() if prog is not None else None

	def get_percent(self):
		return self._ns['percent']

	def set_status(self, status):
		self._ns['status'] = str(status)

	def get_status(self):
		return self._ns['status']

	def set_handler(self, handler):
		self._ns['handler'] = str(handler)

	def get_handler(self):
		return self._ns['handler']

	def set_file(self, file_name):
		self._ns['file_name'] = str(file_name)

	def get_file(self):
		return str(self._ns['file_name'])

	def set_running(self, running):
		self._ns['running'] = True if running else False

	def get_running(self):
		return self._ns['running']

	def set_error(self, err):
		self._ns['error'] = str(err)

	def get_error(self):
		return self._ns['error']

	def clear(self, status="", running=False):
		""" Reset this Progress to the default values. Optionally accepts `status` as a convenience. """
		self._ns['percent'] = None
		self._ns['status'] = status
		self._ns['handler'] = None
		self._ns['running'] = running
		self._ns['file_name'] = None


class LoaderProgress(Progress):
	def __init__(self):
		super().__init__()

	def increment_found(self):
		self._ns['total_found'] = self._ns['total_found'] + 1

	def get_found(self):
		return self._ns['total_found']

	def set_queue_size(self, queue_size):
		self._ns['queue_size'] = queue_size

	def get_queue_size(self):
		return self._ns['queue_size']

	def set_source(self, source):
		self._ns['current_source'] = source

	def get_source(self):
		return self._ns['current_source']

	def set_scanning(self, scanning):
		self._ns['scanning'] = scanning

	def get_scanning(self):
		return self._ns['scanning']

	def clear(self):
		self._ns['queue_size'] = 0
		self._ns['total_found'] = 0
		self._ns['current_source'] = None
		self._ns['scanning'] = True


class ProgressEncoder(json.JSONEncoder):
	# noinspection PyProtectedMember
	def default(self, obj):
		if isinstance(obj, Progress):
			obj = {k: v for (k, v) in obj._ns.items() if not k.startswith("_")}
		elif isinstance(obj, ProgressManifest):
			obj = obj.__dict__
		else:
			return super(ProgressEncoder, self).default(obj)
		return obj


class ProgressManifest:
	"""
	Simple wrapper object for the full Progress Report the Controller object will assemble.
	"""
	def __init__(self, downloaders, loader, deduplication, running):
		self.downloaders = downloaders
		self.loader = loader
		self.deduplication = deduplication
		self.running = running

	def to_obj(self):
		return json.loads(json.dumps(self, cls=ProgressEncoder))


if __name__ == '__main__':
	progg = ProgressManifest(
		downloaders=[DownloaderProgress(), DownloaderProgress()],
		loader=LoaderProgress(),
		deduplication=True,
		running=False
	)
	print(json.dumps(progg.to_obj(), indent=4, sort_keys=True, separators=(',', ': ')))
