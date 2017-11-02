from newspaper import Article, Config
import requests
import mimetypes
import os
import shutil

''' This is (one of) the last-ditch handlers. If all else fails, we attempt to use the Newspaper library to extract the top image from whatever site. '''
tag = 'newspaper'
order = 90000

"""
	TODO: Is it better to fail sometimes, or to get the wrong parse instead?
	This library will almost *certainly* find something to download, even if that image is a really bad option.
	Still, though, it works on sites like Tumblr and other really fringe pages, so it's probably worthwhile to be correct more often than not.
"""

# Return filename/directory name of created file(s), False if a failure is reached, or None if there was no issue, but there are no files.
def handle(url, data):
	try:
		config = Config()
		config.browser_user_agent = data['user_agent']
		article = Article(url, config)
		article.download()
		article.parse()
		if article.top_image:
			print('\t\tNewspaper located image: %s' % article.top_image)
			
			r = requests.get(article.top_image, headers = {'User-Agent': data['user_agent']}, stream=True)
			if r.status_code == 200:
				content_type = r.headers['content-type']
				ext = mimetypes.guess_extension(content_type)
				if not ext or ext=='':
					print('\t\tNewsPaper Error locating file MIME Type: %s' % url)
					return False
				if '.jp' in ext:
					ext = '.jpg'
				path = data['single_file'] % ext
				if not os.path.isfile(path):
					if not os.path.isdir(data['parent_dir']):
						print("\t\t+Building dir: %s" % data['parent_dir'])
						os.makedirs(data['parent_dir'])# Parent dir for the full filepath is supplied already.
					with open(path, 'wb') as f:
						r.raw.decode_content = True
						shutil.copyfileobj(r.raw, f)
				return path
			else:
				print('\t\tError Reading Image: %s responded with code %i!' % (url, r.status_code) )
				return False
	except Exception as e:
		print('\t\t"Newspaper" Generic handler failed. '+(str(e).strip()) )
	return False