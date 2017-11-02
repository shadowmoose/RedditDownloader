import youtube_dl
import stringutil

tag = 'ytdl'
order = 100

file = ''

class Logger(object):
	def debug(self, msg):
		pass

	def warning(self, msg):
		pass

	def error(self, msg):
		if 'Unsupported' not in msg:
			if ';' in msg:
				msg = msg.split(';')[0].strip()
			stringutil.error("\t\tYTDL :: %s" % msg)


def ytdl_hook(d):
	global file
	if '_percent_str' in d:
		print("\t\t+ Downloading:: %s" % d['_percent_str'], end="\r")
	if 'filename' in d:
		file = d['filename']
	
	
	if 'status' in d and d['status'] == 'finished':
		print('\t\t+ Done downloading, now converting ...')


ydl_opts = {
	'outtmpl': './downloaded/%(title)s.%(ext)s',
	'logger': Logger(),
	'progress_hooks': [ytdl_hook],
}

# Return filename/directory name of created file(s), False if a failure is reached, or None if there was no issue, but there are no files.
def handle(url, data):
	global file
	file = ''
	ydl_opts['outtmpl'] = data['single_file'] % '.%(ext)s' # single_file only needs the extension. In this case, use the YTDL ext format.
	ydl_opts['http_headers'] = {'User-Agent': data['user_agent']}
	# noinspection PyBroadException
	try:
		with youtube_dl.YoutubeDL(ydl_opts) as ydl:
			ydl.download([url])
		print("\tCompleted YouTube-DL Download successfully! File: [%s]" % stringutil.fit(file, 75))
		return file
	except Exception:
		# Don't allow the script to crash due to a YTDL exception.
		return False
#