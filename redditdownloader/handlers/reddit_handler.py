tag = 'reddit'
order = 2


def handle(url, data, log):  # !cover
	if 'reddit.com' in url or url.strip().startswith('/r/'):
		return None
	return False
