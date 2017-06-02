# Checks for any invalid authors .
def run_test(re):
	for e in re.elements:
		if e.author != 'theshadowmoose':
			return 'Invalid author name! %s ' % str(e.author), 1;
	return '', 0;