import math;
from bs4 import BeautifulSoup

class StringUtil:
	def fit(input_string, desired_len):
		if desired_len<=3:
			return input_string
		if len(input_string)>desired_len:
			# Trim the input_string to a reasonable length for output:
			h = math.floor(len(input_string)/2);
			input_string = str( input_string[0 : min( math.floor(desired_len/2) - 3, h) ] ) + '...' + str( input_string[ max( math.floor(desired_len/2)*-1 , h*-1) :] );
		return input_string;
	#
	
	def html(html_string, tag='a', tag_val='href'):
		""" Get all the href elements from this HTML string. """
		soup = BeautifulSoup(html_string, 'html.parser')
		urls = [];
		for link in soup.findAll(tag):
			if link.get(tag_val):
				urls.append( str(link.get(tag_val)).strip() );
		return urls;
#