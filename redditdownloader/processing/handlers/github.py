tag = 'github'
order = 2


def handle(task, progress):  # !cover
	if 'github.com' in task.url:
		return None
	return False
