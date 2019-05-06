import math
from bs4 import BeautifulSoup
from colorama import Fore, Style, init
from pprint import pformat
import os.path
import pathvalidate
import sys

init(convert=True, autoreset=True)

_special_colors = {
	'red': Fore.RED,
	'blue': Fore.BLUE,
	'cyan': Fore.CYAN,
	'green': Fore.GREEN,
	'yellow': Fore.YELLOW,
	'magenta': Fore.MAGENTA
}


def fit(input_string, desired_len):  # !cover
	""" Shrinks the given string to fit within the desired_len by collapsing the middle. """
	if desired_len <= 3:
		return input_string  # !cover
	if len(input_string) > desired_len:
		# Trim the input_string to a reasonable length for output:
		h = math.floor(len(input_string)/2)
		input_string = str(input_string[0:min(math.floor(desired_len/2) - 3, h)]) + '...' \
					   + str(input_string[max(math.floor(desired_len/2)*-1, h*-1):])
	return input_string


def html_elements(html_string, tag='a', tag_val='href'):
	""" Get all the href elements from this HTML string. """
	soup = BeautifulSoup(html_string, 'html.parser')
	urls = []
	for link in soup.findAll(tag):
		if link.get(tag_val):
			urls.append(str(link.get(tag_val)).strip())
	return urls


def error(string_output, **kwargs):  # !cover
	print_color('red', string_output, **kwargs)


def print_color(fore_color, string_output, end='\n'):
	"""
	Print the given string with the desired color.
	:param fore_color: Either a string matching a supported color, or a Colorama.Fore color.
	:param string_output: The string to print.
	:param end: The end-of-line character.
	:return:
	"""
	if fore_color.lower() in _special_colors:
		fore_color = _special_colors[fore_color]
	st = "%s%s" % (fore_color+Style.BRIGHT, string_output) + end
	sys.stdout.write(st)


def out(obj, print_val=True, text_color=None):  # !cover
	""" Prints out the given object in the shitty format the Windows Charmap supports. """
	if isinstance(obj, str):
		val = str(obj.encode('ascii', 'ignore').decode('ascii'))
	elif isinstance(obj, (int, float, complex)):
		val = str(obj)
	else:
		val = str(pformat(vars(obj)).encode('ascii', 'ignore').decode('ascii'))
	if text_color is not None:
		val = text_color+str(val)+Style.RESET_ALL
	if print_val:
		print(val)
	return val


def filename(f_name):
	""" Format the given string into an acceptable filename. """
	ret = f_name
	# noinspection PyBroadException
	try:
		ret = pathvalidate.sanitize_filename(ret, '_')
	except Exception:
		ret = '_'
	if len(ret.strip(' .')) == 0:
		return '_'
	return ret


def normalize_file(str_file):
	""" Standardize all paths. Needed in a few spots. """
	return os.path.normpath(str_file.rstrip(' .\n\t'))


def insert_vars(str_path, ele):
	""" Replace the [tagged] ele fields in the given string. Sanitizes inserted values to be filename-compatible. """
	max_len = 200  # We need to leave some headroom for longer (Unknown) extensions and/or naming. !cover
	# TODO: Filename length Test should be implemented to be sure this works cross-platform.
	# TODO: This should replace vars in one pass, to avoid strings with [brackets] messing with it.
	keys = [k for k, v in ele.__dict__.items() if not k.startswith("_")]
	length = min(max_len, max(len(str(ele.__dict__[k])) for k in keys))
	while True:
		ret_str = str_path
		for k, v in ele.__dict__.items():
			if not k.startswith("_"):
				ret_str = ret_str.replace('[%s]' % str(k), ''.join(filename(str(v))[0:length]).strip())

		if len(normalize_file(ret_str)) < max_len:
			return normalize_file(ret_str)
		else:  # !cover
			length -= 1
			if length <= 0:
				error("\t\tFailed to trim file path to acceptable length for Operating System!")
				return None


def is_numeric(s):  # !cover
	""" Check if the given string is numeric """
	try:
		float(s)
		return True
	except ValueError:
		return False
