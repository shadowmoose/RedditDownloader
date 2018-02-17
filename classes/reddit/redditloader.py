import stringutil
from colorama import Fore

class RedditLoader:
	def __init__(self):
		""" Initializes a connector object to the given Reddit account, which instantly attempts to login.
			The script will hang on creating this connection, until the user is signed in.
		"""
		self._elements = []
		self.completed = []
		self.total_count = 0
	#
	
	def scan(self, sources):
		""" Grab all RedditElements from all the supplied Sources """
		self._elements = []
		for source in sources:
			stringutil.print_color(Fore.GREEN, 'Downloading from Source: %s' % source.get_alias())
			for r in source.get_elements():
				r.set_source(source)
				self._elements.append(r)
		self.total_count = len(self._elements)
		print("Element loading complete.\n")


	def count_total(self):
		""" Return the total count of elements. """
		return self.total_count


	def count_remaining(self):
		""" Returns the total number of remaining elements to process. """
		return self.count_total() -  self.count_completed()


	def count_completed(self):
		""" Returns the number of elements already processed. """
		return len(self.completed)


	def get_elements(self):
		""" Generator to return the loaded RedditElements one-by-one, and automatically add them to the "completed" list on finish. Skips duplicates. """
		self._elements.extend(self.completed)# Shuffle back, so this function could be rerun multiple times.
		self.completed = []
		while len(self._elements)>0:
			ele = self._elements.pop(0)
			yield ele
			self.completed.append(ele)


	def url_exists(self, url):
		""" Returns the file name if the given URL has already been processed before. """
		for ele in self.completed:
			if ele.contains_url(url):
				return ele.get_completed_files()[url]
		#
		return None


	def file_exists(self, file_name):
		""" Returns True if the given filename is already used by an Element. """
		return any(ele.contains_file(file_name) for ele in self.completed)


	def get_elements_for_file(self, file_name):
		""" Gets a list of elements that contain the given filename. """
		return [ele for ele in self.completed if ele.contains_file(file_name)]
	