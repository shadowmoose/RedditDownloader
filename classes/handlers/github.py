tag = 'github'
order = 2


def handle(url, data, log):  # !cover
	if 'github.com' in url:
		return None
	return False
