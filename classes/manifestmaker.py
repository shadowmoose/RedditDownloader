import json
import time
from colorama import Fore
import os.path

from stringutil import StringUtil


class ManifestMaker():
	def __init__(self, settings, load = True):
		''' Prepare the Manifest Builder. Optionally load information from the given file. '''
		self.data = {}
		self.file = StringUtil.normalize_file(settings.save_base()+'/Manifest.json')
		if load and os.path.isfile(self.file):
			try:
				with open(self.file) as data_file:
					self.data = json.load(data_file)
			except:
				StringUtil.print_color(Fore.RED, 'Failed to load Manifest at [%s]. Probably corrupt. Try removing the file.' % self.file)
				raise
		#
	#
	
	
	def build(self, loader):
		gen = loader.get_elements()
		
		done = []
		failed = []
		for ele in gen:
			files = ele.get_completed_files()
			if any(False == files[key] for key in files):
				failed.append(ele.to_obj())
			else:
				done.append(ele.to_obj())
		#
		
		with open(self.file, 'w') as outfile:
			obj = {
				'@meta':{
					'version': 2.0,
					'timestamp': time.time(),
					'finished': loader.count_completed() == loader.count_total(),
					'number_completed': loader.count_completed(),
					'number_found' : loader.count_total(),
				},
				'elements':{'completed':done, 'failed':failed},
			}
			json.dump(obj, outfile, sort_keys=True, indent=4, separators=(',', ': '))
	#