from stringutil import StringUtil;
import praw;

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
		self.files = {};
		self.type = None;
		self.id = None;
		self.title = None;
		self.author = None;
		self.urls = [];
		self.subreddit = str(obj.subreddit.display_name);
		self.detect_type(obj);
	
	def detect_type(self, obj):
		''' Simple function to call the proper Comment or Submission handler. '''
		if type(obj) == praw.models.Submission:
			self.submission(obj);
		elif type(obj) == praw.models.reddit.comment.Comment:
			self.comment(obj);
		else:
			print('Unknown Element Type: '+str(type(obj)) );
	#
	
	
	def comment(self, c):
		""" Handle a Comment object. """
		#out("[Comment](%s): %s" % (c.subreddit.display_name, c.link_title) );
		self.type = 'Comment';
		self.id = str(c.link_id);
		self.title = str(c.link_title);
		if c.author:
			self.author = str(c.author.name);
		else:
			self.author = 'Unknown';
		
		for url in StringUtil.html(c.body_html, 'a', 'href'):
			self.add_url(url);
	#
	
	def submission(self, post):
		""" Handle a user's Post. """
		#out("[Post](%s): %s" % (post.subreddit.display_name, post.title) );
		self.type = 'Post';
		self.id = str(post.name);
		self.title = str(post.title);
		if post.author==None:
			self.author = 'Unknown';
		else:
			self.author = str(post.author.name);
		
		if post.selftext!='':
			# This post probably doesn't have a URL, and has selftext instead.
			for url in StringUtil.html(post.selftext_html, 'a', 'href'):
				self.add_url(url)
		if post.url !=None and post.url !='':
			self.add_url(post.url);
	#
	
	def add_file(self, url, file):
		self.files[url] = file;
	
	def add_url(self, url):
		if url not in self.urls:
			self.urls.append(url);
	
	def get_urls(self):
		return self.urls;
		
	def get_completed_files(self):
		return self.files;
	
	def get_json_url(self):
		return 'https://www.reddit.com/api/info.json?id=%s' % self.id;
	
	def to_obj(self):
		ob = {
			'files':self.files,
			'subreddit': self.subreddit,
			'type': self.type,
			'id': self.id,
			'title': self.title,
			'author': self.author,
			'urls': self.urls,
		};
		return ob;