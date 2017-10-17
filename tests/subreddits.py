# Checks for any invalid subreddits .
def run_test(re):
	eles = re.get_elements()
	for e in eles:
		if e.subreddit != 'shadow_test_sub':
			return 'Invalid subreddit name! %s ' % str(e.subreddit), 1
	return '', 0