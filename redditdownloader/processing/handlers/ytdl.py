import youtube_dl
import os
import sys
from processing.handlers import HandlerResponse
from tools import ffmpeg_download
from static import settings
import glob

tag = 'ytdl'
order = 100


class Logger(object):
	def debug(self, msg):
		pass

	def warning(self, msg):
		pass

	def error(self, msg):
		pass


class YTDLWrapper:
	def __init__(self, progress):
		self.files = set()
		self.progress = progress
		self.do_prog_update = True

	def ytdl_hook(self, d):
		if 'filename' in d:
			self.files.add(str(d['filename']))
		if '_percent_str' in d:
			if self.do_prog_update:
				self.do_prog_update = False
				self.progress.set_status("Downloading video...")
			self.progress.set_percent(d['_percent_str'].strip('% '))

	def run(self, url, file):
		tmp_file = file.abs_hashed()
		tmp_hash = os.path.basename(tmp_file)
		file.mkdirs()
		ydl_opts = {
			'logger': Logger(),
			'progress_hooks': [self.ytdl_hook],
			'noplaylist': True,
			'outtmpl': tmp_file + '.%(ext)s',  # single_file only needs the extension.
			'http_headers': {'User-Agent': settings.get('auth.user_agent')},
			'socket_timeout': 10,
			'ffmpeg_location': ffmpeg_download.install_local()
		}
		with youtube_dl.YoutubeDL(ydl_opts) as ydl:
			self.progress.set_status("Looking for video...")
			ydl.download([url])

		# YTDL can mangle paths, so find the temp file it generated.
		tmp_file = glob.glob('%s/**/%s.*' % (file.absolute_base(), tmp_hash), recursive=True)
		if tmp_file:
			tmp_file = tmp_file[0]
			self.files.add(tmp_file)

		failed = not tmp_file or any(str(f).endswith('.unknown_video') for f in self.files)
		if failed:
			for f in self.files:
				if os.path.isfile(f):
					os.remove(f)
			raise Exception("YTDL Download filetype failure.")

		file.set_ext(str(tmp_file).split(".")[-1])
		os.rename(tmp_file, file.absolute())
		return file


# Return filename/directory name of created file(s),
#  False if a failure is reached, or None if there was no issue, but there are no files.
def handle(task, progress):
	# noinspection PyBroadException
	try:
		wrapper = YTDLWrapper(progress)
		file = wrapper.run(task.url, task.file)
		return HandlerResponse(success=True, rel_file=file, handler=tag)
	except Exception as ex:
		if 'unsupported url' not in str(ex).lower():
			print('YTDL:', ex, task.url, file=sys.stderr, flush=True)
		# Don't allow the script to crash due to a YTDL exception.
		return False
