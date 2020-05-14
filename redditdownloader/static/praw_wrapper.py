"""
	Global auth class, for wrapping Praw functionality.
	Access to Praw should be done exclusively through these methods.
"""
import praw
import prawcore
from static import stringutil
from static import settings
from processing.wrappers.redditelement import RedditElement
from praw.models import MoreComments


_credentials = None
_user = None
_reddit = None
_logged_in = False


def check_login(f):
	def wrapper(*xs, **kws):
		if not _logged_in:
			init()
			login()
		return f(*xs, **kws)
	return wrapper


def get_reddit_token_url():
	init()
	return _reddit.auth.url(['identity', 'read', 'history'], settings.get('auth.oauth_key'), 'permanent')


# noinspection PyBroadException
def get_refresh_token(code):
	init()
	try:
		refresh_token = _reddit.auth.authorize(code)
		return refresh_token
	except Exception as ex:
		print(ex)
		return False


def init():
	"""
	Sets the credentials to sign in with.
	"""
	global _reddit
	refresh = None
	if settings.get('auth.refresh_token'):
		refresh = settings.get('auth.refresh_token')
	_reddit = praw.Reddit(
		client_id=settings.get('auth.rmd_client_key'),
		client_secret=None,
		redirect_uri='http://%s:%s/authorize' % (settings.get('interface.host'), settings.get('interface.port')),
		user_agent=settings.get('auth.user_agent'),
		refresh_token=refresh
	)


def login():
	global _user, _logged_in
	if not settings.get('auth.refresh_token'):
		raise ConnectionError('Missing the Refresh Token from Reddit! Cannot auth.')
	stringutil.print_color('yellow', "Authenticating via OAuth...")
	_user = _reddit.user.me()
	stringutil.print_color('yellow', "Authenticated as [%s]\n" % _user.name)
	_logged_in = True


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


@check_login
def get_current_username():
	return _user.name


@check_login
def my_liked_saved():
	""" Get the upvoted/saved posts & comments for the signed-in user. """
	if not _user:
		raise ConnectionError('User not signed in!')
	yield from user_liked_saved(_user.name)


@check_login
def user_liked_saved(username, scan_upvoted=True, scan_saved=True, scan_sub=None):
	""" Gets all the upvoted/saved comments and/or submissions for the given User. Allows filtering by Subreddit. """
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


@check_login
def subreddit_posts(sub, order_by='new', limit=None, time='all'):
	""" Get Posts from the given subreddit, with PRAW-based filtering & sorting options. """
	yield from _praw_apply_filter(_reddit.subreddit(sub), order_by, limit, time)


@check_login
def frontpage_posts(order_by='new', limit=None, time='all'):
	""" Get Posts from the authed account's front page, with PRAW-based filtering & sorting options. """
	yield from _praw_apply_filter(_reddit.front, order_by, limit, time)


@check_login
def user_posts(username, find_submissions, find_comments):
	""" Generator for all the posts made by the given Redditor. """
	try:
		if find_comments:
			for c in _reddit.redditor(username).comments.new():
				yield RedditElement(c)
		if find_submissions:
			for c in _reddit.redditor(username).submissions.new():
				yield RedditElement(c)
	except prawcore.exceptions.NotFound:
		stringutil.error('Cannot locate comments or submissions for nonexistent user: %s' % username)


@check_login
def multi_reddit(username, reddit_name, order_by='new', limit=None, time='all'):
	""" Generator to get Submissions from a User-curated MultiReddit. """
	yield from _praw_apply_filter(_reddit.multireddit(username, reddit_name), order_by, limit, time)


@check_login
def get_submission_comments(t3_id):
	""" Implemented initially for converting invalid IDs.
	Returns a generator of top comments from the given Submission. """
	submission = get_submission(t3_id=t3_id)
	for top_level_comment in submission.comments:
		if isinstance(top_level_comment, MoreComments):
			continue
		setattr(top_level_comment, 'link_title', submission.title)
		setattr(top_level_comment, 'over_18', submission.over_18)
		setattr(top_level_comment, 'num_comments', submission.num_comments)
		setattr(top_level_comment, 'score', submission.score)
		yield top_level_comment


@check_login
def get_submission(t3_id):
	if not t3_id.startswith('t3_'):
		raise Exception('Invalid submission id: %s' % t3_id)
	t3_id = t3_id.replace('t3_', '', 1)  # Convert to expected format.
	return _reddit.submission(id=t3_id)


@check_login
def get_comment(t1_id):
	if not t1_id.startswith('t1_'):
		raise Exception('Invalid Comment id: %s' % t1_id)
	t1_id = t1_id.replace('t1_', '', 1)  # Convert to expected format.
	return _reddit.comment(id=t1_id)


@check_login
def get_info(fullnames):
	"""
	A generator to get the Submission/Comment from the given array of full IDs.
	:param fullnames: Full (prefixed) reddit IDs.
	:return: An array of Comments+Submissions.
	"""
	return _reddit.info(fullnames)


@check_login
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
