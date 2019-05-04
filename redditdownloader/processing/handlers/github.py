tag = 'github'
order = 1


def handle(task, progress):  # !cover
	if 'github.com' in task.url:
		return None
	return False
