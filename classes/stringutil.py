import math
from bs4 import BeautifulSoup
from colorama import Fore, Style
import string
from pprint import pformat
import os.path

def fit(input_string, desired_len):
	if desired_len<=3:
		return input_string
	if len(input_string)>desired_len:
		# Trim the input_string to a reasonable length for output:
		h = math.floor(len(input_string)/2)
		input_string = str( input_string[0 : min( math.floor(desired_len/2) - 3, h) ] ) + '...' + str( input_string[ max( math.floor(desired_len/2)*-1 , h*-1) :] )
	return input_string
#

def html_elements(html_string, tag='a', tag_val='href'):
	""" Get all the href elements from this HTML string. """
	soup = BeautifulSoup(html_string, 'html.parser')
	urls = []
	for link in soup.findAll(tag):
		if link.get(tag_val):
			urls.append( str(link.get(tag_val)).strip() )
	return urls

def html(html_string, tag='a', tag_val='href'):
	""" TODO: This is a polyfill so I can commit a few changes without breaking old Parsers... This will be removed when I get a more comprehensive updater. """
	return html_elements(html_string, tag, tag_val)

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
#


def filename(f_name):
	""" Format the given string into an acceptable filename. """
	valid_chars = "-_.() %s%s[]" % (string.ascii_letters, string.digits)
	return ''.join(c for c in f_name if c in valid_chars)
#

def normalize_file(str_file):
	""" Standardize all paths. Needed in a few spots. """
	return os.path.normpath(str_file)

def insert_vars(str_path, ele):
	""" Replace the [tagged] ele fields in the given string. Sanitizes any inserted values to be filename-compatible. """
	for k,v in ele.to_obj().items():
		str_path = str_path.replace('[%s]' % str(k), filename(str(v)) )
	str_path = normalize_file(str_path)
	return str_path
#