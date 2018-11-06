
from classes.sources.frontpage_posts_source import FrontpagePostsSource
from classes.sources.multireddit_source import MultiRedditSource
from classes.sources.my_upvoted_saved_source import UpvotedSaved
from classes.sources.subreddit_posts_source import SubredditPostsSource
from classes.sources.user_posts_source import UserPostsSource
from classes.sources.user_upvoted_saved_source import UserUpvotedSaved


def all_sources():
	return [
		FrontpagePostsSource(),
		MultiRedditSource(),
		UpvotedSaved(),
		SubredditPostsSource(),
		UserPostsSource(),
		UserUpvotedSaved()
	]


def load_sources(source_list=None):
	"""
	Get a list of all availale Sources.

	Expects that source_list is the direct array of Sources loaded from settings.
	"""
	loaded = []
	if source_list is None:
		return all_sources()
	else:
		for s in source_list:
			for l in all_sources():
				if l.from_obj(s):
					loaded.append(l)
					break
	return loaded
