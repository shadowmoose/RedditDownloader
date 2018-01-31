import math
from bs4 import BeautifulSoup
from colorama import Fore, Style
import string
from pprint import pformat
import os.path

def fit(input_string, desired_len):
	""" Shrinks the given string to fit within the desired_len by collapsing the middle. """
	if desired_len<=3:
		return input_string
	if len(input_string)>desired_len:
		# Trim the input_string to a reasonable length for output:
		h = math.floor(len(input_string)/2)
		input_string = str( input_string[0 : min( math.floor(desired_len/2) - 3, h) ] ) + '...' + str( input_string[ max( math.floor(desired_len/2)*-1 , h*-1) :] )
	return input_string


def html_elements(html_string, tag='a', tag_val='href'):
	""" Get all the href elements from this HTML string. """
	soup = BeautifulSoup(html_string, 'html.parser')
	urls = []
	for link in soup.findAll(tag):
		if link.get(tag_val):
			urls.append( str(link.get(tag_val)).strip() )
	return urls


def error(string_output, **kwargs):
	print_color(Fore.RED, string_output, **kwargs)


def print_color(fore_color, string_output, **kwargs):
	""" Print() the given string colored as desired. """
	print(fore_color+string_output+Style.RESET_ALL, **kwargs)


def out(obj, print_val=True):
	""" Prints out the given object in the shitty format the Windows Charmap supports. """
	if isinstance(obj, str):
		val = str(obj.encode('ascii', 'ignore').decode('ascii') )
	elif isinstance(obj, (int, float, complex)):
		val = str(obj)
	else:
		val = str(pformat(vars(obj)).encode('ascii', 'ignore').decode('ascii') )
	if print_val:
		print(val)
	return val


def filename(f_name):
	""" Format the given string into an acceptable filename. """
	valid_chars = "-_.() %s%s[]&" % (string.ascii_letters, string.digits)
	return ''.join(c for c in f_name if c in valid_chars)


def normalize_file(str_file):
	""" Standardize all paths. Needed in a few spots. """
	return os.path.normpath(str_file)


def insert_vars(str_path, ele):
	""" Replace the [tagged] ele fields in the given string. Sanitizes inserted values to be filename-compatible. """
	max_len = 1000
	if os.name == 'nt':
		max_len = 230 # We need to leave some headroom for longer (Unknown) extensions and/or naming.
	length = min(max_len, max(len(v) for k,v in ele.to_obj().items()) )
	while True:
		ret_str = str_path
		for k,v in ele.to_obj().items():
			ret_str = ret_str.replace('[%s]' % str(k),''.join(filename(str(v))[0:length]).strip() )

		if len(os.path.abspath(ret_str) ) < max_len:
			return normalize_file(ret_str)
		length -=1
		if length <= 0:
			error("\t\tFailed to trim file path to acceptable length for Operating System!")
			return None


def is_numeric(s):
	""" Check if the given string is numeric """
	try:
		float(s)
		return True
	except ValueError:
		return False