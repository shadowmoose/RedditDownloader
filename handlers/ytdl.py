from __future__ import unicode_literals
import youtube_dl
from stringutil import StringUtil as su;

tag = 'ytdl';
order = 100;

file = '';

class MyLogger(object):
	def debug(self, msg):
		pass

	def warning(self, msg):
		pass

	def error(self, msg):
		if 'Unsupported' not in msg:
			su.error("\t\tYTDL :: %s" % msg)


def ytdl_hook(d):
	global file;
	if '_percent_str' in d:
		print("\t\t+ Downloading:: %s" % d['_percent_str'], end="\r");
	if 'filename' in d:
		file = d['filename'];
	
	
	if 'status' in d and d['status'] == 'finished':
		print('\t\t+ Done downloading, now converting ...');


ydl_opts = {
	'outtmpl': './downloaded/%(title)s.%(ext)s',
	'logger': MyLogger(),
	'progress_hooks': [ytdl_hook],
}

# Return filename/directory name of created file(s), False if a failure is reached, or None if there was no issue, but there are no files.
def handle(url, data):
	global file;
	file = '';
	ydl_opts['outtmpl'] = data['single_file'] % '.%(ext)s'; # single_file only needs the extension. In this case, use the YTDL ext format.
	ydl_opts['http_headers'] = {'User-Agent': data['user_agent']};
	try:
		with youtube_dl.YoutubeDL(ydl_opts) as ydl:
			ydl.download([url]);
		print("\tCompleted YouTube-DL Download successfully! File: [%s]" % file);
		return file;
	except KeyboardInterrupt:
		raise
	except:
		return False;
	return False;
#