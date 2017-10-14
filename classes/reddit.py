import praw;
from stringutil import StringUtil as SU;
from colorama import Fore

from redditelement import RedditElement


class RedditLoader():
	def __init__(self, client_id, client_secret, password, username, user_agent):
		''' Initializes a connector object to the given Reddit account, which instantly attempts to login.
			The script will hang on creating this connection, until the user is signed in.
		'''
		self._elements = []
		self.completed = []
		self.total_count = 0
		
		SU.print_color(Fore.YELLOW, "Authenticating via OAuth...")
		
		self.reddit = praw.Reddit(client_id=client_id, client_secret=client_secret, password=password, user_agent=user_agent, username=username)
		self.user = self.reddit.user.me()
		
		SU.print_color(Fore.YELLOW, "Authenticated as [%s]\n" % self.user.name)
	#
	
	def scan(self):
		''' Grab all saved Comments and Posts in advance, to avoid timeouts '''
		if not self.user:
			return
		
		SU.print_color(Fore.CYAN, 'Loading Saved Comments & Posts...')
		for saved in self.user.saved(limit=None):
			re = RedditElement(saved)
			if re not in self._elements:
				self._elements.append(re)
		
		SU.print_color(Fore.CYAN, 'Loading Upvoted Comments & Posts...')
		for upvoted in self.user.upvoted(limit=None):
			re = RedditElement(upvoted)
			if re not in self._elements:
				self._elements.append(re)
		
		self.total_count = len(self._elements)
		print("Element loading complete.\n")
	#
	
	def count_total(self):
		''' Return the total count of elements. '''
		return self.total_count
	
	def count_remaining(self):
		''' Returns the total number of remaining elements to process. '''
		return self.count_total() -  self.count_completed()
	
	def count_completed(self):
		''' Returns the number of elements already processed. '''
		return len(self.completed)
	
	def get_elements(self):
		''' Generator to return the loaded RedditElements one-by-one, and automatically add them to the "completed" list on finish. Skips duplicates. '''
		self._elements.extend(self.completed)# Shuffle back, so this function could be rerun multiple times.
		self.completed = []
		while len(self._elements)>0:
			ele = self._elements.pop(0)
			yield ele
			self.completed.append(ele)
	#
	
	def url_exists(self, url):
		''' Returns the file name if the given URL has already been processed before. '''
		for ele in self.completed:
			if ele.contains_url(url):
				return ele.get_completed_files()[url]
		#
		return None
	
	def file_exists(self, file_name):
		''' Returns True if the given filename is already used by an Element. '''
		return any(ele.contains_file(file_name) for ele in self.completed)
	