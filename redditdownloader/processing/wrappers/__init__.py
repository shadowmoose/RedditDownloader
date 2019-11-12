import json
from processing.wrappers.rel_file import RelFile, SanitizedRelFile
from processing.wrappers.queue_reader import QueueReader
from multiprocessing import Array
import ctypes


class AckPacket:
	def __init__(self, url_id, extra_urls):
		self.url_id = url_id
		self.extra_urls = extra_urls


class Progress:
	"""
	Progress is a wrapper for multiprocessing's Array class.
	It is capable of syncing status across multiple Processes, almost 10x faster than a Manager class.

	This class specifically uses getters and setters, in order to avoid improperly mutating shared data.
	"""

	def __init__(self, field_size=200):
		self.field_size = field_size
		self.fields = {f: Array(ctypes.c_char, self.field_size) for f in self.get_fields()}
		self.clear()

	def clear(self):
		pass

	def get_fields(self):
		return []

	def set(self, field, value):
		if isinstance(value, str) and len(value) > (self.field_size - 2):
			value = value[:self.field_size - 5].strip() + '...'
		value = json.dumps(value)
		if len(value) > self.field_size:
			value = json.dumps(("[META: Encoding Error: %s.%s]" % (self.__class__.__name__, field))[:self.field_size-2])
		self.fields[field].value = value.encode(errors='replace')
		return True

	def get(self, field):
		return json.loads(self.fields[field].value.decode(errors='replace').strip() or 'null')


class DownloaderProgress(Progress):
	def __init__(self):
		super().__init__()

	def set_percent(self, prog):
		return self.set('percent', str(prog).strip() if prog is not None else None)

	def get_percent(self):
		return self.get('percent')

	def set_status(self, status):
		return self.set('status', str(status))

	def get_status(self):
		return self.get('status')

	def set_handler(self, handler):
		return self.set('handler', str(handler))

	def get_handler(self):
		return self.get('handler')

	def set_file(self, file_name):
		return self.set('file_name', str(file_name))

	def get_file(self):
		return self.get('file_name')

	def set_running(self, running):
		return self.set('running', bool(running))

	def get_running(self):
		return self.get('running')

	def set_error(self, err):
		self.set('error', str(err))

	def get_error(self):
		return self.get('error')

	def clear(self, status="", running=False):
		""" Reset this Progress to the default values. Optionally accepts `status` as a convenience. """
		self.set('percent', None)
		self.set('status', status)
		self.set('handler', None)
		self.set('running', running)
		self.set('file_name', None)

	def get_fields(self):
		return ['percent', 'status', 'handler', 'running', 'file_name', 'error']


class LoaderProgress(Progress):
	def __init__(self):
		super().__init__()

	def increment_found(self):
		return self.set('total_found', self.get('total_found') + 1)

	def get_found(self):
		return self.get('total_found')

	def set_queue_size(self, queue_size):
		return self.set('queue_size', queue_size)

	def get_queue_size(self):
		return self.get('queue_size')

	def set_source(self, source):
		return self.set('current_source', source)

	def get_source(self):
		return self.get('current_source')

	def set_scanning(self, scanning):
		return self.set('scanning', scanning)

	def get_scanning(self):
		return self.get('scanning')

	def clear(self):
		self.set('queue_size', 0)
		self.set('total_found', 0)
		self.set('current_source', None)
		self.set('scanning', True)

	def get_fields(self):
		return ['queue_size', 'total_found', 'current_source', 'scanning']


class ProgressEncoder(json.JSONEncoder):
	# noinspection PyProtectedMember
	def default(self, obj):
		if isinstance(obj, Progress):
			obj = {k: obj.get(k) for k in obj.fields.keys()}
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
	dlp = DownloaderProgress()
	dlp.set_handler({k: 'val' for k in range(1000)})
	progg = ProgressManifest(
		downloaders=[dlp, DownloaderProgress()],
		loader=LoaderProgress(),
		deduplication=True,
		running=False
	)
	print(json.dumps(progg.to_obj(), indent=4, sort_keys=True, separators=(',', ': ')))
