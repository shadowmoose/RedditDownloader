# Checks for any invalid authors .
def run_test(re):
	eles = re.get_elements()
	for e in eles:
		if e.author != 'theshadowmoose' and e.author != 'test_reddit_scraper':
			return 'Invalid author name! %s ' % str(e.author), 1  # !cover
	return '', 0
