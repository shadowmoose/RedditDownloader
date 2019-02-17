tag = 'reddit'
order = 2


def handle(task):  # !cover
	if 'reddit.com' in task.url or task.url.strip().startswith('/r/'):
		return None
	return False
