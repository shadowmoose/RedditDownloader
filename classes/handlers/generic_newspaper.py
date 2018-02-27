from newspaper import Article, Config
import requests
import mimetypes
import os
import shutil

''' This is (one of) the last-ditch handlers. If all else fails, we attempt to use the Newspaper library to extract the top image from whatever site. '''
tag = 'newspaper'
order = 90000

"""
	Is it better to fail sometimes, or to get the wrong parse instead?
	This library will almost *certainly* find something to download, even if that image is a really bad option.
	Still, though, it works on sites like Tumblr and other really fringe pages, so it's probably worthwhile to be correct more often than not.
"""

# Return filename/directory name of created file(s), False if a failure is reached, or None if there was no issue, but there are no files.
def handle(url, data, log):
	try:
		log.out(0,'Downloading article...')
		resp = requests.get(url, headers = {'User-Agent': data['user_agent']})
		if resp.status_code != 200:
			return False #!cover

		config = Config()
		config.memoize_articles = False
		config.verbose = False
		article = Article(url='', config=config)
		log.out(0,'Parsing article...')

		article.download()
		article.set_html(resp.text)
		article.parse()
		if article.top_image:
			src = article.top_image
			if 'http' not in src: #!cover
				if 'https' in url:
					src = 'https://' + src.lstrip('/ ').strip()
				else:
					src = 'http://'  + src.lstrip('/ ').strip()
			log.out(0, 'Newspaper located image: %s' % src)
			
			r = requests.get(src, headers = {'User-Agent': data['user_agent']}, stream=True)
			if r.status_code == 200:
				content_type = r.headers['content-type']
				ext = mimetypes.guess_extension(content_type)
				if not ext or ext=='': #!cover
					log.out(1, 'NewsPaper Error locating file MIME Type: %s' % url)
					return False
				if '.jp' in ext:
					ext = '.jpg' #!cover
				path = data['single_file'] % ext
				if not os.path.isfile(path):
					if not os.path.isdir(data['parent_dir']): #!cover
						log.out(1, ("+Building dir: %s" % data['parent_dir']))
						os.makedirs(data['parent_dir'])# Parent dir for the full filepath is supplied already.
					with open(path, 'wb') as f:
						r.raw.decode_content = True
						shutil.copyfileobj(r.raw, f)
				return path
			else: #!cover
				log.out(0,('\t\tError Reading Image: %s responded with code %i!' % (url, r.status_code) ))
				return False
	except Exception as e:
		log.out(0, ('"Newspaper" Generic handler failed. '+(str(e).strip()) ) )
	return False #!cover


if __name__ == '__main__':
	url_t = input("Target URL: ").strip()
	data_t = {
		'single_file':'./test%s',
		'parent_dir':'../',
		'user_agent':'test-agent'
	}
	import processing.logger as logger
	print('Result:', handle(url_t, data_t, logger.Logger())   )
