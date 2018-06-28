"""
	Global auth class, for wrapping Praw functionality.
	Access to Praw should be done exclusively through these methods.
"""
import praw
import prawcore
from colorama import Fore
from classes.static import stringutil
from classes.processing.redditelement import RedditElement

_credentials = None
_user = None
_reddit = None


def init(client_id, client_secret, password, username, user_agent):
	"""
	Sets the credentials to sign in with.
	"""
	global _credentials
	_credentials = {
		'client_id': client_id,
		'client_secret': client_secret,
		'password': password,
		'user_agent': user_agent,
		'username': username
	}


def login():
	global _credentials, _user, _reddit
	if not _credentials:
		raise ConnectionError('Credentials not set!')

	stringutil.print_color(Fore.LIGHTYELLOW_EX, "Authenticating via OAuth...")
	_reddit = praw.Reddit(**_credentials)
	_user = _reddit.user.me()
	stringutil.print_color(Fore.LIGHTYELLOW_EX, "Authenticated as [%s]\n" % _user.name)


def post_orders():
	""" Returns a list of tuples, indicating acceptable Order values and if they accept Time limits or not. """
	return [
		('top', True),
		('best', False),
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


def my_liked_saved():
	""" Get the upvoted/saved posts & comments for the signed-in user. """
	global _user
	if not _user:
		raise ConnectionError('User not signed in!')
	yield from user_liked_saved(_user.name)


def user_liked_saved(username, scan_upvoted=True, scan_saved=True, scan_sub=None):
	""" Gets all the upvoted/saved comments and/or submissions for the given User. Allows filtering by Subreddit. """
	global _reddit, _user
	params = {'sr': scan_sub} if scan_sub else None
	try:
		if _user.name.lower() == username.lower():
			redditor = _user
		else:
			redditor = _reddit.redditor(username)
		if scan_saved:
			for saved in redditor.saved(limit=None, params=params):
				re = RedditElement(saved)
				yield re

		if scan_upvoted:
			for upvoted in redditor.upvoted(limit=None, params=params):
				re = RedditElement(upvoted)
				yield re
	except prawcore.exceptions.NotFound:
		stringutil.error('Cannot locate comments or submissions for nonexistent user: %s' % username)
	except prawcore.Forbidden:
		stringutil.error('Cannot load Upvoted/Saved Posts from the User "%s", because they are private!' % username)


def subreddit_posts(sub, order_by='new', limit=None, time='all'):
	""" Get Posts from the given subreddit, with PRAW-based filtering & sorting options. """
	global _reddit
	yield from _praw_apply_filter(_reddit.subreddit(sub), order_by, limit, time)


def frontpage_posts(order_by='new', limit=None, time='all'):
	""" Get Posts from the authed account's front page, with PRAW-based filtering & sorting options. """
	global _reddit
	yield from _praw_apply_filter(_reddit.front, order_by, limit, time)


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


def get_submission_comments(t3_id):
	""" Implemented initially for converting invalid IDs.
	Returns a generator of top comments from the given Submission. """
	assert t3_id.startswith('t3_')
	t3_id = t3_id.lstrip('t3_')  # Convert to expected format.
	submission = _reddit.submission(id=t3_id)
	for top_level_comment in submission.comments:
		yield top_level_comment


def _praw_apply_filter(praw_object, order_by='new', limit=None, time='all'):
	""" Accepts a Praw object (subreddit/multireddit/user posts/etc) and applies filters to it. Returns a Generator. """
	order = [o for o in post_orders() if o[0] == order_by]
	assert len(order) > 0  # The order must be a valid value.
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
