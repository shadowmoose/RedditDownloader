import youtube_dl
import os
from handlers import HandlerResponse
from static import settings

tag = 'ytdl'
order = 100


class Logger(object):
	def debug(self, msg):
		pass

	def warning(self, msg):
		pass  # !cover

	def error(self, msg):
		pass  # !cover


class YTDLWrapper:
	def __init__(self, progress):
		self.file = None
		self.progress = progress
		self.do_prog_update = True

	def ytdl_hook(self, d):
		if 'filename' in d:
			self.file = str(d['filename'])
		if '_percent_str' in d:
			if self.do_prog_update:
				self.do_prog_update = False
				self.progress.set_status("Downloading video...")
			self.progress.set_percent(d['_percent_str'].replace('%', ''))

	def run(self, task):
		task.file.mkdirs()
		ydl_opts = {
			'logger': Logger(),
			'progress_hooks': [self.ytdl_hook],
			'outtmpl': task.file.absolute() + '.%(ext)s',  # single_file only needs the extension.
			'http_headers': {'User-Agent': settings.get('auth.user_agent')},
			'socket_timeout': 10
		}
		with youtube_dl.YoutubeDL(ydl_opts) as ydl:
			self.progress.set_status("Looking for video...")
			ydl.download([task.url])

		if self.file and str(self.file).endswith('.unknown_video'):
			# File downloaded as unknown type - failure.
			if os.path.isfile(self.file):
				os.remove(self.file)
			raise Exception("YTDL Download filetype failure.")
		task.file.set_ext(str(self.file).split(".")[-1])
		return task.file


# Return filename/directory name of created file(s),
#  False if a failure is reached, or None if there was no issue, but there are no files.
def handle(task, progress):
	# noinspection PyBroadException
	try:
		wrapper = YTDLWrapper(progress)
		file = wrapper.run(task)
		return HandlerResponse(success=True, rel_file=file, handler=tag)
	except Exception:
		# Don't allow the script to crash due to a YTDL exception.
		return False
