import sys;
sys.path.insert(0, './handlers')
sys.path.insert(0, './util')

import praw;
from pprint import pformat
import os;
import re;
import string;
from stringutil import StringUtil;
import json;

handlers = [];
for module in os.listdir('./handlers/'):
	if module == '__init__.py' or module[-3:] != '.py':
		continue
	lib = __import__(module[:-3], locals(), globals())
	handlers.append(lib);
#
handlers.sort(key=lambda x: x.order, reverse=False);
print("Loaded handlers: ", ', '.join([x.tag for x in handlers]) );

download_dir = "./download/";
settings_file = './settings.json';

def out(obj):
	""" Prints out the given object in the shitty format the Windows Charmap supports. """
	if isinstance(obj, str):
		print(obj.encode('ascii', 'ignore').decode('ascii') );
	elif isinstance(obj, (int, float, complex)):
		print(obj);
	else:
		print(pformat(vars(obj)).encode('ascii', 'ignore').decode('ascii') );
#

class Scraper():
	reddit = None;
	me = None;
	
	all_reddit = [];# List of all posts we've liked/saved. Stored initially to avoid timeouts.
	file_map = {};# Maps all URLs to their downloaded filenames.
	
	urls = [];
	failed = [];

	def init(self):
		''' Authenticate and prepare to scan. '''
		info = self.load_settings();
		if not info:
			self.build_settings();
			print('Please configure the generated settings file before launching again.');
			print('Fill in your username/password, and register an app here: https://www.reddit.com/prefs/apps\n Fill the app\'s information in as well.');
			return;
		print("Authenticating via OAuth...");
		self.reddit = praw.Reddit(client_id=info['client_id'], client_secret=info['client_secret'],password=info['password'], user_agent=info['user_agent'], username=info['username']);
		self.me = self.reddit.user.me();
		print("Authenticated as [%s]" % self.me.name)
	
	def load_settings(self):
		if not os.path.isfile(settings_file):
			return None;
		with open(settings_file) as json_data:
			d = json.load(json_data)
			return d;
	
	def build_settings(self):
		''' Build a dummy Settings file. '''
		obj = {'client_id':'ID_From_Registering_app', 'client_secret':"Secret_from_registering_app",'password':'Your_password', 'user_agent':'USE_A_RANDOM_ID_HERE','username':'Your_Username'};
		with open(settings_file, 'w') as outfile:
			json.dump(obj, outfile)
	
	def scan(self):
		''' Grab all saved Comments and Posts in advance, then start checking them all. '''
		if not self.me:
			return;
		print('Loading Saved Comments & Posts...');
		for saved in self.me.saved(limit=None):
			self.all_reddit.append(saved);
		print('Loading Upvoted Comments & Posts...');
		for upvoted in self.me.upvoted(limit=None):
			self.all_reddit.append(upvoted);
		self.run();
	
	def run(self):
		''' Run through all saved Comments and Posts, and process them into URLs. '''
		try:
			i = 1;
			for saved in self.all_reddit:
				print("%i/%i: " % (i, len(self.all_reddit) ), end="")
				self.detect_type(saved);
				i+=1;
		except KeyboardInterrupt:
			print("Interrupted.");
		print('=============================== All URLS LOCATED =============================')
		for u in self.urls:
			out(u);
		print('================================= FILE MAP ===================================')
		for k, v in self.file_map.items():
			print("["+str(k)+"] = ["+str(v)+"]")
		print(" =============================== FAILED URLS =================================");
		for u in self.failed:
			out(u);
	#
	
	def detect_type(self, obj):
		''' Simple function to call the proper Comment or Submission handler. '''
		if type(obj) == praw.models.Submission:
			self.submission(obj);
		elif type(obj) == praw.models.reddit.comment.Comment:
			self.comment(obj);
		else:
			print(type(obj));
		print();
	#
	
	
	def comment(self, c):
		""" Handle a Comment object. """
		out("[Comment](%s): %s" % (c.subreddit.display_name, c.link_title) );
		for url in StringUtil.html(c.body_html, 'a', 'href'):
			self.process_url(url, c.subreddit.display_name, c.link_title, c.author.name);
	#
	
	def submission(self, post):
		""" Handle a user's Post. """
		out("[Post](%s): %s" % (post.subreddit.display_name, post.title) );
		author = post.author;
		if author==None:
			author = 'Unknown';
		else:
			author = author.name;
		if post.selftext!='':
			# This post probably doesn't have a URL, and has selftext instead.
			for url in re.findall(r'(https?://\S+)', post.selftext):
				self.process_url(url, post.subreddit.display_name, post.title, author);
		if post.url !=None and post.url !='':
			self.process_url(post.url, post.subreddit.display_name, post.title, author);
	#
	
	def filename(self, filename):
		''' Format the givne string into an acceptable filename. '''
		valid_chars = "-_.() %s%s[]" % (string.ascii_letters, string.digits)
		return ''.join(c for c in filename if c in valid_chars);
	
	def process_url(self, url, subreddit, title, author):
		'''  Accepts a URL and Post/Comment details, then runs through the Handlers loaded from the other directory, attempting to download the url.  '''
		out("\tProcessing URL: %s" % url);
		if url not in self.urls:
			self.urls.append(url);
		else:
			print("\t\t+URL already taken care of.")
			return True;
		basedir = download_dir+self.filename(subreddit)+"/";
		basefile = basedir+self.filename(title)+" - ("+self.filename(author)+')';
		og = basefile;
		i=2;
		while next((s for s in self.file_map.values() if basefile in s), None):
			print("\t!Incrementing duplicate filename.")
			basefile = og+' . '+str(i)+' ';
		data = {
			'parent_dir'	: basedir,			# Some handlers will need to build the parent directory for their single file first. This simplifies parsing.
			'single_file'	: basefile+"%s",	# If this handler can output a single file, it will use this path.
			'multi_dir' 	: basefile+"/",		# If the handler is going to download multiple files, it will save them under this directory.
			'post_title'	: title,			# The title of the Reddit post.
			'post_subreddit': subreddit,		# The subreddit this post came from.
		};
		
		for h in handlers:
			out("\tChecking handler: %s" % h.tag);
			ret = h.handle(url, data)
			if ret==None:
				# None is returned when the handler specifically wants this URL to be "finished", but not added to the files list.
				out("\t+Handler '%s' completed correctly, but returned no files!" % h.tag )
				return True;
			if ret:
				out("\t+Handler '%s' completed correctly! %s" % (h.tag, StringUtil.fit(ret, 75)) )
				self.file_map[url] = ret;
				# The handler will return a file/directory name if it worked properly.
				return True;
		self.failed.append(url);
		return False;
	#
#

p = Scraper();
p.init();
p.scan();