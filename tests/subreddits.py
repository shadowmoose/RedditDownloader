# Checks for any invalid subreddits .
def run_test(re):
	for e in re.elements:
		if e.subreddit != 'shadow_test_sub':
			return 'Invalid subreddit name! %s ' % str(e.subreddit), 1;
	return '', 0;