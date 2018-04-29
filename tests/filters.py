import classes.sources.test_producer as test_source
import classes.filters.filter as filters
import time

# Tests loading Posts from Sources, and filtering them.
start_time = time.time()

filter_dict = {
	"created_utc.max": start_time,
	"score.min": 1000,
	"title.match": "re",
	"url_pattern.match":'.com'
}


def run_test(re):
	fl = filters.get_filters(filter_dict)
	#print('\n\n')
	ts = test_source.TestPostProducer()
	ts.apply_filters(fl)

	loaded_posts = []
	for e in ts.get_elements():
		loaded_posts.append(e)
		#print(e.title)

	if len(loaded_posts) == 0:
		return 'No posts were matched by test filters!', 5

	for p in loaded_posts:
		#print(p.title)
		if p.created_utc > start_time:
			return 'Invalid parsed time!', 1 # Shouldn't happen, but that's why we test.
		if 're' not in p.title.lower():
			return 'Invalid title!', 2
		if p.score < 1000:
			return 'Invalid score: %s' % p.score, 3
		if not any('.com' in url.lower() for url in p.get_urls()):
			return 'Invalid URL found in Post.', 4

	return '', 0
