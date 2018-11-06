import classes.sources.test_producer as test_source
from classes import filters
import time

# Tests general Filter capability loading Filters from a JSON-style dict, then filtering Posts from the Test Source.
start_time = time.time()

filter_dict = {
	"created_utc.max": start_time,
	"score.min": 1000,
	"title.match": "re",
	"url_pattern.match": '\.com'
}


def run_test(re):
	fl = filters.get_filters(filter_dict)
	if len(fl) != 4:
		return 'Built incorrect list of Filters: %s' % fl, 6
	# print('\n\n')
	ts = test_source.TestPostProducer()
	ts.apply_filters(fl)

	loaded_posts = []
	for e in ts.get_elements():
		loaded_posts.append(e)
		# print(e.title)

	if len(loaded_posts) == 0:
		return 'No posts were matched by test filters!', 5

	for p in loaded_posts:
		# print(p.title)
		if p.created_utc > start_time:
			return 'Invalid parsed time!', 1
		if 're' not in p.title.lower():
			return 'Invalid title!', 2
		if p.score < 1000:
			return 'Invalid score: %s' % p.score, 3
		if any('.com' not in url.lower() for url in p.get_urls()):
			return 'Invalid URL found in Post.', 4

	return '', 0
