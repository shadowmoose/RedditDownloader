"""  File to repair any invalid directories RMD may have created, specifically only impacting Windows users. """

import os

def get_short_path_name(long_name):
	"""
	Gets the short path name of a given long path.
	http://stackoverflow.com/a/23598461/200291
	"""
	output_buf_size = 0
	import ctypes
	from ctypes import wintypes
	_GetShortPathNameW = ctypes.windll.kernel32.GetShortPathNameW
	_GetShortPathNameW.argtypes = [wintypes.LPCWSTR, wintypes.LPWSTR, wintypes.DWORD]
	_GetShortPathNameW.restype = wintypes.DWORD
	while True:
		output_buf = ctypes.create_unicode_buffer(output_buf_size)
		needed = _GetShortPathNameW(long_name, output_buf, output_buf_size)
		if output_buf_size >= needed:
			return output_buf.value
		else:
			output_buf_size = needed



def repair_subdirs(parent):
	if os.name != 'nt':
		print("This is only for Windows, as it is the only platform to experience the bug this fixes.")
		return
	dirs = ([x[0] for x in os.walk(parent)])
	dirs = sorted(dirs, reverse=True)# Should put subdirs first.
	for d in dirs:
		short = get_short_path_name(d)
		d = os.path.abspath(d)
		filename = os.path.basename(d.rstrip('/\\'))
		parent = os.path.dirname(d)
		new_file = parent+'/'+filename.strip().rstrip(' .-')
		# noinspection PyBroadException
		try:
			os.rename(short, new_file)
			print("Renamed file: [%s]  ->  [%s]  (Short: %s)" % (d, new_file, short))
		except:
			print("Hit error renaming directory: ", d)
			pass



if __name__ == '__main__':
	if os.name != 'nt':
		print("This is only for Windows, as it is the only platform to experience the bug this fixes.")
		import sys
		sys.exit(1)
	print('\nThis is a mini program to (attempt to) repair buggy Windows directories.')
	print('It scans all the subdirectories in the directory you specify,\n'
		  'including the selected directory, and attempts to rename them to valid Windows names.')
	print("This should ONLY be run if you're stuck with some directories that can't be removed or renamed.")
	print("\nAdditionally, this only works on Windows platforms, and has only been tested on Win10.")
	print("\tIf you're having issues with directories on other Operating Systems, it's not a bug this can fix.")
	print()
	if 'y' in input('Are you sure you want to run this? (y/n): ').lower():
		targ = input('Enter the EXACT PATH to the base directory you want scanned: ')
		targ = os.path.abspath(targ)
		if 'y' in input('Is the path "%s" correct? (y/n): ' % targ).lower():
			repair_subdirs(targ)
		else:
			print("Aborted run.")
		print('Finished.')
	else:
		print('Not running.')