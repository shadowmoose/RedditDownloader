
from sources.frontpage_posts_source import FrontpagePostsSource
from sources.multireddit_source import MultiRedditSource
from sources.my_upvoted_saved_source import UpvotedSaved
from sources.subreddit_posts_source import SubredditPostsSource
from sources.user_posts_source import UserPostsSource
from sources.user_upvoted_saved_source import UserUpvotedSaved
from sources.pushshift_subreddit import PushShiftSubmissionSource
from sources.pushshift_user_posts import PushShiftUserSourceSource
from sources.direct_input_source import DirectInputSource
from sources.direct_url_source import DirectURLSource
from sources.pushshift_search_source import PushShiftSearchSource


def all_sources():
	return [
		FrontpagePostsSource(),
		MultiRedditSource(),
		UpvotedSaved(),
		SubredditPostsSource(),
		UserPostsSource(),
		UserUpvotedSaved(),
		PushShiftSubmissionSource(),
		PushShiftUserSourceSource(),
		PushShiftSearchSource()
	]


def load_sources(source_list=None):
	"""
	Get a list of all available Sources.

	Expects that source_list is the direct array of Sources loaded from settings.
	"""
	loaded = []
	if source_list is None:
		return all_sources()
	else:
		for s in source_list:
			for l in all_sources() + [DirectInputSource(), DirectURLSource()]:
				if l.from_obj(s):
					loaded.append(l)
					break
			else:
				raise Exception("Unable to load Source: %s" % s)
	return loaded
