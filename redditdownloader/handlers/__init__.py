from static import stringutil


def sorted_list():
	""" A list of all available static Handlers, pre-sorted by order. """
	from handlers import github, imgur, generic_newspaper, reddit_handler, ytdl
	return sorted([
		generic_newspaper, github, imgur, reddit_handler, ytdl
	], key=lambda x: x.order, reverse=False)


class HandlerTask:
	def __init__(self, url, file_obj):
		self.url = url
		self.file = file_obj


class HandlerResponse:
	def __init__(self, success, handler, rel_file=None, failure_reason=None, album_urls=()):
		self.rel_file = rel_file
		self.success = success
		self.handler = handler
		self.failure_reason = failure_reason
		self.album_urls = album_urls


def handle(handler_task):
	"""
	Pass the given HandlerTask into the handler list, and try to find one that can download the given file.
	"""
	for h in sorted_list():
		try:
			result = h.handle(handler_task)
			if result:
				return result
		except Exception as ex:  # There are too many possible exceptions between all handlers to catch properly.
			stringutil.error('Handler [%s] :: {%s} :: %s' % (h.tag, handler_task.url, ex))
			# We don't *really* care if a Handler fails, since there are plenty of reasons a download could.
			pass
	return HandlerResponse(success=False, handler=None, failure_reason="No Handlers could process this URL.")
