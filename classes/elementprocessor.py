from redditelement import RedditElement
from stringutil import StringUtil as SU
from colorama import Fore, Style
import os


class ElementProcessor():
	''' The heavy-lifting bit. Handles processing all the Elements provided to it via the generator it's created with, by finding the most appropriate Handler for each Element. '''
	
	def __init__(self, reddit_loader, settings):
		''' Creates and prepares the Processor object, with the given RedditLoader to provide RedditElements. Takes a loaded Settings object to find the configured save path. '''
		self.loader = reddit_loader
		self.gen = self.loader.get_elements()
		self.settings = settings
		self.handlers = []
		self.load_handlers()
	#
	
	def load_handlers(self):
		''' Loads all the available handlers from the handler directory. '''
		self.handlers = []
		for module in os.listdir('handlers'):
			if module == '__init__.py' or module[-3:] != '.py':
				continue
			lib = __import__(module[:-3], locals(), globals())
			self.handlers.append(lib)
		#
		self.handlers.sort(key=lambda x: x.order, reverse=False)
		print("Loaded handlers: ", ', '.join([x.tag for x in self.handlers]) )
	#
	
	def run(self):
		for ele in self.gen:
			self.process_ele(ele)
	#
	
	
	def process_ele(self, re):
		''' Accepts a RedditElement of Post/Comment details, then runs through the Handlers loaded from the other directory, attempting to download the url.  '''
		print('%i/%i: ' % (self.loader.count_completed()+1, self.loader.count_total() ), end='')
		SU.print_color(Fore.YELLOW, SU.out("[%s](%s): %s" % (re.type, re.subreddit, re.title), False) )
		
		for url in re.get_urls():
			print('\tURL: %s' % url)
			if self.loader.url_exists(url):
				SU.print_color(Fore.GREEN, "\t\t+URL already taken care of.")
				re.add_file(url, 'Duplicate')
				continue
			base_file, file_info = self.build_file_info(re)# Build the file information array using this RedditElement's information
			file_path = self.process_url(url, file_info)
			re.add_file(url, base_file)# Add this completed file information to the Element
	#
	
	
	def process_url(self, url, info):
		''' Accepts a URL and the array of file info generated for it by this class, and then attempts to download it using any possible handler.
			Returns whatever the handlers do, which should be a path to the file itself or the contianing directory for an album.
				+Also returns False or None if no appropriate handler was found, or if the handler told us not to download anything.
		'''
		ret_val = False # Default to 'False', meaning no file was located by a handler.
		for h in self.handlers:
			print("\tChecking handler: %s" % h.tag)
			ret = h.handle(url, info)
			if ret==None:
				# None is returned when the handler specifically wants this URL to be "finished", but not added to the files list.
				SU.print_color(Fore.GREEN, "\t+Handler '%s' completed correctly, but returned no files!" % h.tag )
				ret_val = None
				break
			if ret:
				SU.out("%s\t+Handler '%s' completed correctly! %s%s" % (Fore.GREEN, h.tag, SU.fit(ret, 75), Style.RESET_ALL) )
				# The handler will return a file/directory name if it worked properly.
				ret_val = ret
				break
			#
		#
		return ret_val
	#
	
	def build_file_info(self, re):
		''' Generates an array of file locations and element data that is passed down to every handler, so they can choose where best to save for themselves. '''
		dir_pattern  = '%s/%s' % ( self.settings.save_base() , self.settings.save_subdir() )
		file_pattern = '%s/%s' % ( dir_pattern, self.settings.save_filename())
		
		basedir = SU.insert_vars(dir_pattern, re)
		basefile = SU.insert_vars(file_pattern, re)
		
		og = basefile
		i=2
		while self.loader.file_exists(basefile) or re.contains_file(basefile):
			print("\t!Incrementing duplicate filename. (%s)" % i, end='\r')
			basefile = og+' . '+str(i)+' '
			i+=1
		if i>2:
			print('')
		
		return basefile, {
			'parent_dir'	: basedir,			# Some handlers will need to build the parent directory for their single file first. This simplifies parsing.
			'single_file'	: basefile+"%s",	# If this handler can output a single file, it will use this path.
			'multi_dir' 	: basefile+"/",		# If the handler is going to download multiple files, it will save them under this directory.
			'post_title'	: re.title,			# The title of the Reddit post.
			'post_subreddit': re.subreddit,		# The subreddit this post came from.
			'user_agent'	: self.settings.get('auth', None)['user_agent'],
		}