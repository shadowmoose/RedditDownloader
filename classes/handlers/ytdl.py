import youtube_dl
from util import stringutil

tag = 'ytdl'
order = 100

class Logger(object):
	def debug(self, msg):
		pass

	def warning(self, msg):
		pass #!cover

	def error(self, msg):
		pass #!cover
		# if 'Unsupported' not in msg:
			#if ';' in msg:
			#	msg = msg.split(';')[0].strip()
			#stringutil.error("\t\tYTDL :: %s" % msg)


class YTDLWrapper:
	def __init__(self, log):
		self.file = None
		self.log = log


	def ytdl_hook(self, d):
		if '_percent_str' in d:
			self.log.out(0, 'Downloading video...')
			self.log.out(1,"+ Downloading:: %s" % d['_percent_str'])
		if 'filename' in d:
			self.file = d['filename']
		if 'status' in d and d['status'] == 'finished':
			self.log.out(1, '+ Done downloading, now converting ...')


	def run(self, url, data):
		ydl_opts = {
			'logger': Logger(),
			'progress_hooks': [self.ytdl_hook],
			'outtmpl': data['single_file'] % '.%(ext)s', # single_file only needs the extension. In this case, use the YTDL ext format.
			'http_headers': {'User-Agent': data['user_agent']}
		}
		with youtube_dl.YoutubeDL(ydl_opts) as ydl:
			ydl.download([url])
		self.log.out(0, "Completed YouTube-DL Download successfully! File: [%s]" % stringutil.fit(self.file, 75))
		return self.file


# Return filename/directory name of created file(s), False if a failure is reached, or None if there was no issue, but there are no files.
def handle(url, data, log):
	log.out(0, "Preparing YTDL Handler...")
	# noinspection PyBroadException
	try:
		log.out(0, 'Grabbing video information...')
		wrapper = YTDLWrapper(log)
		file = wrapper.run(url, data)
		log.out(0, "Completed YouTube-DL Download successfully! File: [%s]" % stringutil.fit(file, 75))
		return file
	except Exception:
		# Don't allow the script to crash due to a YTDL exception.
		return False
#