from bs4 import BeautifulSoup
from colorama import Fore, Style, init
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


def html_elements(html_string, tag='a', tag_val='href'):
	""" Get all the href elements from this HTML string. """
	soup = BeautifulSoup(html_string, 'html.parser')
	urls = []
	for link in soup.findAll(tag):
		if link.get(tag_val):
			urls.append(str(link.get(tag_val)).strip())
	return urls


def error(string_output, **kwargs):
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


def is_numeric(s):
	""" Check if the given string is numeric """
	try:
		float(s)
		return True
	except ValueError:
		return False
