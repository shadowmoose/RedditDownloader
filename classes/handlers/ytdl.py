import youtube_dl
import stringutil

tag = 'ytdl'
order = 100

class Logger(object):
	def debug(self, msg):
		pass

	def warning(self, msg):
		pass

	def error(self, msg):
		if 'Unsupported' not in msg:
			if ';' in msg:
				msg = msg.split(';')[0].strip()
			#stringutil.error("\t\tYTDL :: %s" % msg)



# Return filename/directory name of created file(s), False if a failure is reached, or None if there was no issue, but there are no files.
def handle(url, data, log):
	# noinspection PyBroadException
	try:
		file = ''
		def ytdl_hook(d):
			global file
			if '_percent_str' in d:
				log.out(1,"+ Downloading:: %s" % d['_percent_str'])
			if 'filename' in d:
				file = d['filename']
			if 'status' in d and d['status'] == 'finished':
				log.out(1, '+ Done downloading, now converting ...')
		ydl_opts = {
			'logger': Logger(),
			'progress_hooks': [ytdl_hook],
			'outtmpl': data['single_file'] % '.%(ext)s', # single_file only needs the extension. In this case, use the YTDL ext format.
			'http_headers': {'User-Agent': data['user_agent']}
		}
		with youtube_dl.YoutubeDL(ydl_opts) as ydl:
			ydl.download([url])
		log.out(0, "Completed YouTube-DL Download successfully! File: [%s]" % stringutil.fit(file, 75))
		return file
	except Exception:
		# Don't allow the script to crash due to a YTDL exception.
		return False
#