import stringutil
import praw.models
import copy

class RedditElement(object):
	"""
		A wrapper class to store & process Reddit Post/Comment data.
		Attributes:
			type: A String of this element's original type, either "Post" or "Comment".
			id: A string representing the (Post 'name' or Comment 'link_id') of this element.
			subreddit: A string representing the subreddit name owning this element.
			title: A string representing the title of the Post belonging to this element.
			author: string representing the author of this element.
			_urls: A String Array of urls parsed for this post/comment.
	"""

	def __init__(self, obj):
		""" Creates the object. Automatically calls its own detect_type() function to resolve variable name mappings. """
		self._file_map = {}
		self._urls = []
		self.type = None
		self.id = None
		self.title = None
		self.author = None
		self.body = None
		self.subreddit = str(obj.subreddit.display_name)
		self.detect_type(obj)

		self.over_18 = obj.over_18
		self.created_utc = obj.created_utc
		self.num_comments = obj.num_comments
		self.score = obj.score
		self.link_count = len(self._urls)
		self.source_alias = None

		assert self.type is not None
		assert self.id is not None


	def detect_type(self, obj):
		""" Simple function to call the proper Comment or Submission handler. """
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
			self.author = 'Deleted'
		self.body = c.body
		for url in stringutil.html_elements(c.body_html, 'a', 'href'):
			self.add_url(url)
	#


	def submission(self, post):
		""" Handle a Submission. """
		#out("[Post](%s): %s" % (post.subreddit.display_name, post.title) )
		self.type = 'Submission'
		self.id = str(post.name)
		self.title = str(post.title)
		if post.author is None:
			self.author = 'Deleted'
		else:
			self.author = str(post.author.name)
		self.body = post.selftext
		if post.selftext.strip() != '':
			# This post probably doesn't have a URL, and has selftext instead.
			for url in stringutil.html_elements(post.selftext_html, 'a', 'href'):
				self.add_url(url)
		if post.url is not None and post.url.strip() != '':
			self.add_url(post.url)
	#


	def add_file(self, url, file):
		""" add a url and it's file location to this element. Signifies that this URL is completed. """
		self._file_map[url] = file


	def add_url(self, url):
		""" Add a URL to this element. """
		if url not in self._urls:
			self._urls.append(url)


	def remove_url(self, url):
		if url in self._urls:
			self._urls.remove(url)
		else:
			print("Cannot remove:", url)
		if url in self._file_map:
			del self._file_map[url]


	def set_source(self, source_obj):
		"""  Sets this Element's source alias by pulling it directly from the object.  """
		self.source_alias = str(source_obj.get_alias())


	def get_id(self):
		""" Get this element's ID. """
		return self.id


	def get_urls(self):
		""" Returns a list of all this element's UNIQUE urls. """
		return self._urls[:]


	def get_completed_files(self):
		""" Returns deep copy of the [url]=[files] dict built for the completed URLs of this element.
		Can be a bit expensive to call. """
		return copy.deepcopy(self._file_map)


	def get_json_url(self):
		""" Returns the API access point for this comment's JSON. """
		return 'https://www.reddit.com/api/info.json?id=%s' % self.id


	def contains_url(self, url):
		""" if this element contains the given URL. """
		return url in self._file_map


	def contains_file(self, file_name):
		""" if this element contains the given file name. """
		return any(file_name in str(self._file_map[key]) for key in self._file_map)


	def remap_file(self, filename_old, filename_new):
		""" Remap an old filename to a new one. """
		for f in self._file_map:
			if self._file_map[f] == filename_old:
				self._file_map[f] = filename_new


	def to_obj(self):
		""" we use this to translate the element into a simple, constant layout for template variables and JSON output. """
		ob = {
			'files':self.get_completed_files(),
			'subreddit': self.subreddit,
			'type': self.type,
			'id': self.id,
			'title': self.title,
			'author': self.author,
			'urls': self.get_urls(),
			'source_alias': self.source_alias,
		}
		return ob