# Checks for any invalid authors .
def run_test(re):
	eles = re.get_elements()
	for e in eles:
		if e.author != 'theshadowmoose':
			return 'Invalid author name! %s ' % str(e.author), 1
	return '', 0