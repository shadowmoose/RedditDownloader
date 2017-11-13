"""
	Global auth class, for wrapping Praw functionality.
	Access to Praw should be done exclusively through these methods.
"""
import praw
import stringutil
from colorama import Fore
from redditelement import RedditElement

_credentials = None
_user = None
_reddit = None

def init( client_id, client_secret, password, username, user_agent):
	"""
	Sets the credentials to sign in with.
	"""
	global _credentials
	_credentials = {
		'client_id':client_id,
		'client_secret':client_secret,
		'password':password,
		'user_agent':user_agent,
		'username':username
	}


def login():
	global _credentials, _user, _reddit
	if not _credentials:
		raise ConnectionError('Credentials not set!')

	stringutil.print_color(Fore.YELLOW, "Authenticating via OAuth...")
	_reddit = praw.Reddit(**_credentials)
	_user = _reddit.user.me()
	stringutil.print_color(Fore.YELLOW, "Authenticated as [%s]\n" % _user.name)


def my_liked_saved():
	""" Get the  upvoted/saved posts & comments for the signed-in user. """
	global _user
	if not _user:
		raise ConnectionError('User not signed in!')
	_elements = []
	stringutil.print_color(Fore.CYAN, 'Loading Saved Comments & Posts...')
	for saved in _user.saved(limit=None):
		re = RedditElement(saved)
		if re not in _elements:
			_elements.append(re)

	stringutil.print_color(Fore.CYAN, 'Loading Upvoted Comments & Posts...')
	for upvoted in _user.upvoted(limit=None):
		re = RedditElement(upvoted)
		if re not in _elements:
			_elements.append(re)
	return _elements


def post_orders():
	""" Returns a list of tuples, indicating acceptable Order values and if they accept Time limits or not. """
	return [
		('top', True),
		('new', False),
		('hot', False),
		('controversial', True),
		('gilded', False),
		('rising', False),
	]


def time_filters():
	return [
		'all', 'hour', 'day', 'month', 'week', 'year'
	]


def subreddit_posts(sub, order_by='new', limit=None, time='all'):
	""" Get Posts from the given subreddit, with PRAW-based filtering & sorting options. """
	global _reddit
	order = [o for o in post_orders() if o[0] == order_by]
	assert len(order) > 0 # The order must be a valid value.
	assert time in time_filters()
	if limit < 1:
		limit = None
	order = order[0]
	try:
		sr = _reddit.subreddit(sub) # Build object for query
		if not order[1]:
			gen = getattr(sr, order[0])(limit=limit)
		else:
			gen = getattr(sr, order[0])(limit=limit, time_filter=time)
		for g in gen:
			yield RedditElement(g)
	except TypeError as e:
		stringutil.error('Invalid subreddit order configuration! [%s]' % order_by)
		print(order)
		print(e)