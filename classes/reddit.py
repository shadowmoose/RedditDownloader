"""
	Global auth class, for wrapping Praw functionality.
	Access to Praw should be done exclusively through these methods.
"""
import praw
import prawcore
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
	""" Get the upvoted/saved posts & comments for the signed-in user. """
	global _user
	if not _user:
		raise ConnectionError('User not signed in!')
	yield from user_liked_saved(_user.name)


def user_liked_saved(username, scan_upvoted=True, scan_saved=True):
	""" Gets all the upvoted/saved comments and/or submissions for the given User. """
	global _reddit, _user
	try:
		if _user.name.lower() == username.lower():
			redditor = _user
		else:
			redditor = _reddit.redditor(username)
		if scan_saved:
			stringutil.print_color(Fore.CYAN, '\tLoading %s\'s Saved Posts...' % redditor.name)
			for saved in redditor.saved(limit=None):
				re = RedditElement(saved)
				yield re

		if scan_upvoted:
			stringutil.print_color(Fore.CYAN, '\tLoading %s\'s Upvoted Posts...' % redditor.name)
			for upvoted in redditor.upvoted(limit=None):
				re = RedditElement(upvoted)
				yield re
	except prawcore.exceptions.NotFound:
		stringutil.error('Cannot locate comments or submissions for nonexistent user: %s' % username)
	except prawcore.Forbidden:
		stringutil.error('Cannot load Upvoted/Saved Posts from the User "%s", because they are private!' % username)


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
	""" Returns a list of valid Reddit timespans, which can be applied to most ListingGenerators """
	return [
		'all', 'hour', 'day', 'week', 'month', 'year'
	]


def subreddit_posts(sub, order_by='new', limit=None, time='all'):
	""" Get Posts from the given subreddit, with PRAW-based filtering & sorting options. """
	global _reddit
	yield from _praw_apply_filter(_reddit.subreddit(sub), order_by, limit, time)


def user_posts(username, find_submissions, find_comments):
	""" Generator for all the posts made by the given Redditor. """
	global _reddit
	try:
		if find_comments:
			for c in _reddit.redditor(username).comments.new():
				yield RedditElement(c)
		if find_submissions:
			for c in _reddit.redditor(username).submissions.new():
				yield RedditElement(c)
	except prawcore.exceptions.NotFound:
		stringutil.error('Cannot locate comments or submissions for nonexistent user: %s' % username)


def multi_reddit(username, reddit_name, order_by='new', limit=None, time='all'):
	""" Generator to get Submissions from a User-curated MultiReddit. """
	global _reddit
	yield from _praw_apply_filter(_reddit.multireddit(username, reddit_name), order_by, limit, time)


def _praw_apply_filter(praw_object, order_by='new', limit=None, time='all'):
	""" Accepts a Praw object (subreddit/multireddit/user posts/etc) and applies filters to it. Returns a Generator. """
	order = [o for o in post_orders() if o[0] == order_by]
	assert len(order) > 0 # The order must be a valid value.
	assert time in time_filters()
	if limit < 1:
		limit = None
	order = order[0]
	try:
		if not order[1]:
			gen = getattr(praw_object, order[0])(limit=limit)
		else:
			gen = getattr(praw_object, order[0])(limit=limit, time_filter=time)
		for g in gen:
			yield RedditElement(g)
	except TypeError as e:
		stringutil.error('Invalid Praw order configuration! [%s]' % order_by)
		print(order)
		print(e)