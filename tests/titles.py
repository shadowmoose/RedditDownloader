# Checks for any invalid titles .
def run_test(re):
	for e in re.elements:
		if 'Test' not in e.title:
			return 'Invalid Post title! %s ' % str(e.title), 1;
	return '', 0;