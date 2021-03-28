import praw.models
from static import stringutil
import re
import json
import html
from ttp import ttp

url_parser = ttp.Parser()


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
			body: The body of text iin this Post.
			parent: The ID of this Post's parent Submission, if this Element is a Comment. Otherwise NULL.
	"""

	def __init__(self, obj, ext_submission_obj=None):
		""" Creates the object. Automatically calls its own detect_type() function to resolve variable name mappings. """
		self._urls = []
		self._ext_submission = ext_submission_obj
		self.type = None
		self.id = None
		self.title = None
		self.author = None
		self.body = None
		self.parent = None
		self.subreddit = None
		self.over_18 = None
		self.num_comments = None
		self.score = None
		self.detect_type(obj)

		self.created_utc = obj.created_utc
		self.link_count = len(self._urls)
		self.source_alias = None

		assert self.type == 'Submission' or self.type == 'Comment'
		assert self.id is not None
		assert not self.parent or 't3_' in self.parent
		assert 't1_' in self.id or 't3_' in self.id

	def detect_type(self, obj):
		""" Simple function to call the proper Comment or Submission handler. """
		# noinspection PyUnresolvedReferences
		tp = type(obj)
		stp = str(tp).lower()
		if type(obj) == praw.models.Submission:
			self._submission(obj)
		elif type(obj) == praw.models.reddit.comment.Comment:
			self._comment(obj)
		elif 'submission' in stp:
			self._ps_submission(obj)
		elif 'comment' in stp:
			self._ps_comment(obj)
		else:
			raise Exception('Unknown Element Type: '+str(type(obj)))
	
	def _comment(self, c):
		""" Handle a Comment object. """
		# out("[Comment](%s): %s" % (c.subreddit.display_name, c.link_title) )
		self.type = 'Comment'
		self.id = str(c.fullname)
		self.parent = self._comment_field(c, 'link_id', 'fullname')
		self.title = self._comment_field(c, 'link_title', 'title')
		self.subreddit = str(c.subreddit.display_name)
		if c.author:
			self.author = str(c.author.name)
		else:
			self.author = 'Deleted'
		self.over_18 = self._comment_field(c, 'over_18', 'over_18')
		self.num_comments = self._comment_field(c, 'num_comments', 'num_comments')
		self.score = self._comment_field(c, 'score', 'score')
		self.body = c.body
		for url in stringutil.html_elements(c.body_html, 'a', 'href'):
			self.add_url(url)

	def _ps_comment(self, c):
		""" Handle a Pushshift Comment object. """
		# out("[Comment](%s): %s" % (c.subreddit.display_name, c.link_title) )
		self.type = 'Comment'
		self.id = c.id
		if 't1_' not in self.id:
			self.id = 't1_%s' % self.id
		self.parent = self._comment_field(c, 'link_id', 'fullname')
		self.title = self._comment_field(c, 'link_title', 'title')
		self.subreddit = c.subreddit
		if c.author is None or c.author == '[deleted]':
			self.author = 'Deleted'
		else:
			self.author = str(c.author)
		self.over_18 = self._comment_field(c, 'over_18', 'over_18')
		self.num_comments = self._comment_field(c, 'num_comments', 'num_comments')
		self.score = self._comment_field(c, 'score', 'score')
		self.body = html.unescape(str(c.body))
		if self.body.strip():
			bod = self.body
			for u in re.findall(r'\[.+?\]\s*?\((.+?)\)', bod):
				# The ttp plaintext parser does a bad job with [special](urls), so pre-locate & remove them.
				self.add_url(u)
				bod = bod.replace(u, '', 1)
			result = url_parser.parse(bod)
			for u in result.urls:
				self.add_url(u)

	def _submission(self, post):
		""" Handle a Submission. """
		# out("[Post](%s): %s" % (post.subreddit.display_name, post.title) )
		self.type = 'Submission'
		self.id = str(post.fullname)
		self.title = str(post.title)
		self.subreddit = str(post.subreddit.display_name)
		if post.author is None:
			self.author = 'Deleted'
		else:
			self.author = str(post.author.name)
		self.over_18 = post.over_18
		self.num_comments = post.num_comments
		self.score = post.score
		self.body = post.selftext
		if post.selftext.strip() != '':
			# This post probably doesn't have a URL, and has selftext instead.
			for url in stringutil.html_elements(post.selftext_html, 'a', 'href'):
				self.add_url(url)
		if getattr(post, 'is_gallery', False) and getattr(post, 'media_metadata', False):
			for k, img in post.media_metadata.items():
				try:
					self.add_url(img['s']['u'])
				except:
					stringutil.error('Unable to parse URL from reddit album.')
		elif post.url is not None and post.url.strip() != '':
			self.add_url(post.url)

	def _ps_submission(self, post):
		""" Handle a PushShift Submission. """
		self.type = 'Submission'
		self.id = post.id
		if 't3_' not in self.id:
			self.id = 't3_%s' % self.id
		self.title = post.title
		self.subreddit = post.subreddit
		if getattr(post, 'author', None) is None or post.author == '[deleted]':
			self.author = 'Deleted'
		else:
			self.author = str(post.author)
		self.over_18 = post.over_18
		self.num_comments = post.num_comments
		self.score = post.score
		self.body = html.unescape(str(post.selftext)) if 'selftext' in post and post.selftext else ''
		if getattr(post, 'is_gallery', False) and getattr(post, 'media_metadata', False):
			for k, img in post.media_metadata.items():
				try:
					self.add_url(html.unescape(img['s']['u']))
				except:
					stringutil.error('Unable to parse URL from praw reddit album');
		elif post.url is not None and post.url.strip() != '' and 'reddit.com' not in post.url:
			self.add_url(post.url)
		if self.body.strip():
			for u in re.findall(r'\[.+?\]\s*?\((.+?)\)', self.body):
				self.add_url(u)

	def _comment_field(self, obj, attr, backup):
		if hasattr(obj, attr):
			return getattr(obj, attr)
		else:
			sub = self._get_submission_obj(obj)
			val = getattr(sub, backup)
			if sub == self._ext_submission and isinstance(val, str):
				return html.unescape(val)
			return val

	def _get_submission_obj(self, obj):
		""" Get the "submission" property of the given object, or fall back to the _ext_submission object. """
		sub = obj.submission if hasattr(obj, 'submission') else self._ext_submission
		if not sub:
			raise Exception("Comment object is missing Submission, and has no extra provided!")
		return sub

	def add_url(self, url):
		""" Add a URL to this element. """
		if any(url.strip().startswith(x) for x in ['/u/', '/r/']):
			return
		if url not in self._urls:
			self._urls.append(url)

	def remove_url(self, url):
		if url in self._urls:
			self._urls.remove(url)
		else:
			print("Cannot remove:", url)

	def set_source(self, source_obj):
		"""  Sets this Element's source alias by pulling it directly from the object.  """
		self.source_alias = str(source_obj.get_alias())

	def get_id(self):
		""" Get this element's ID. """
		return self.id

	def get_urls(self):
		""" Returns a list of all this element's UNIQUE urls. """
		return self._urls[:]

	def __str__(self):
		return json.dumps(self.__dict__)
