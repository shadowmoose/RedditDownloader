# Checks for any invalid titles .
def run_test(re):
	eles = re.get_elements()
	for e in eles:
		if 'Test' not in e.title:
			return 'Invalid Post title! %s ' % str(e.title), 1
	return '', 0