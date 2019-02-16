from enum import Enum
from filters.filter import Filter

from filters.created_utc_filter import UTCFilter
from filters.url_match_filter import URLFilter


class Operators(Enum):
	""" Enum for porting around operators. """
	EQUALS = '.equals'
	MINIMUM = '.min'
	MAXIMUM = '.max'
	MATCH = '.match'


def custom_filters():
	return [UTCFilter(), URLFilter()]


def filter_fields():
	""" Builds a list of acceptable fields to filter Elements by. """
	return {
		'link_count': 'The amount of links found for this element. (#)',
		'type': 'The type of post this is. ("Submission" or "Comment")',
		'title':  'The title of the submission containing this post. (Text)',
		'author': 'The author of this element. (Text)',
		'body':  'The text in this element. Blank if this post is a submission without selftext. (Text)',
		'subreddit': 'The subreddit this element is from. (Text)',
		'over_18': 'If this post is age-limited, AKA "NSFW". (True/False)',
		'created_utc': 'The timestamp, in UTC seconds, that this element was posted. (#)',
		'num_comments': 'The number of comments on this post. (#)',
		'score': 'The number of net upvotes on this post. (#)',
	}


def get_filters(filter_dict=None):
	""" Get a list of all availale Filter objects.
		If passed a dict of {'field.operator':val} - as specified by the filter settings syntax -
			it will return loaded filter objects.
	"""
	loaded = []
	if filter_dict is None:
		loaded = custom_filters()
		used = set(l.field for l in loaded)
		for k, v in filter_fields().items():
			if k in used:
				continue
			used.add(k)
			cl = Filter(field=k, description=v)  # New filter for default values.
			loaded.append(cl)
	else:
		for loaded_field, loaded_value in filter_dict.items():
			for f in get_filters(None):
				if f.from_obj(loaded_field, loaded_value):
					loaded.append(f)
					break
	return loaded
