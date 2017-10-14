from stringutil import StringUtil
from colorama import Fore, Style
import praw

class RedditElement(object):
	"""
		A wrapper class to store & process Reddit Post/Comment data.
		Attributes:
			type: A String of this element's original type, either "Post" or "Comment".
			id: A string representing the (Post 'name' or Comment 'link_id') of this element.
			subreddit: A string representing the subreddit name owning this element.
			title: A string representing the title of the Post belonging to this element.
			author: string representing the author of this element.
			urls: A String Array of urls parsed for this post/comment.
	"""
	
	def __init__(self, obj):
		''' Creates the object. Automatically calls its own detect_type() function to resolve variable name mappings. '''
		self.files = {}
		self.type = None
		self.id = None
		self.title = None
		self.author = None
		self.urls = []
		self.subreddit = str(obj.subreddit.display_name)
		self.detect_type(obj)
	
	def detect_type(self, obj):
		''' Simple function to call the proper Comment or Submission handler. '''
		if type(obj) == praw.models.Submission:
			self.submission(obj)
		elif type(obj) == praw.models.reddit.comment.Comment:
			self.comment(obj)
		else:
			print('Unknown Element Type: '+str(type(obj)) )
	#
	
	
	def comment(self, c):
		""" Handle a Comment object. """
		#out("[Comment](%s): %s" % (c.subreddit.display_name, c.link_title) )
		self.type = 'Comment'
		self.id = str(c.link_id)
		self.title = str(c.link_title)
		if c.author:
			self.author = str(c.author.name)
		else:
			self.author = 'Unknown'
		
		for url in StringUtil.html_elements(c.body_html, 'a', 'href'):
			self.add_url(url)
	#
	
	def submission(self, post):
		""" Handle a user's Post. """
		#out("[Post](%s): %s" % (post.subreddit.display_name, post.title) )
		self.type = 'Post'
		self.id = str(post.name)
		self.title = str(post.title)
		if post.author==None:
			self.author = 'Unknown'
		else:
			self.author = str(post.author.name)
		
		if post.selftext!='':
			# This post probably doesn't have a URL, and has selftext instead.
			for url in StringUtil.html_elements(post.selftext_html, 'a', 'href'):
				self.add_url(url)
		if post.url !=None and post.url !='':
			self.add_url(post.url)
	#
	
	def add_file(self, url, file):
		''' add a url and it's file location to this element. Signifies that this URL is completed. '''
		self.files[url] = file
	
	def add_url(self, url):
		''' Add a URL to this element. '''
		if url not in self.urls:
			self.urls.append(url)
	
	def get_id():
		'''get this element's ID. '''
		return self.id
	
	def get_urls(self):
		''' returns a list of all this element's UNIQUE urls. '''
		return self.urls
		
	def get_completed_files(self):
		''' Returns the [url]=[files] array build for the completed URLs of this element. '''
		return self.files
	
	def get_json_url(self):
		''' Returns the API access point for this comment's JSON. '''
		return 'https://www.reddit.com/api/info.json?id=%s' % self.id
	
	
	def contains_url(self, url):
		''' if this element contains the given URL. '''
		return url in self.get_completed_files()
	
	def contains_file(self, file_name):
		''' if this element contains the given file name. '''
		files = self.get_completed_files()
		return any(file_name in str(files[key]) for key in files)
	
	def to_obj(self):
		''' we use this to translate the element into a simple, constant layout for template variables and JSON output. '''
		ob = {
			'files':self.get_completed_files(),
			'subreddit': self.subreddit,
			'type': self.type,
			'id': self.id,
			'title': self.title,
			'author': self.author,
			'urls': self.urls,
		}
		return ob