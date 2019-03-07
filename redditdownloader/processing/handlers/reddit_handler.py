tag = 'reddit'
order = 2


def handle(task, progress):  # !cover
	if 'reddit.com' in task.url or any(task.url.strip().startswith(p) for p in ['/r/', '/u/']):
		return None
	return False
