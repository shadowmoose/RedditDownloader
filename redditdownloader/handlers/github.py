tag = 'github'
order = 2


def handle(task):  # !cover
	if 'github.com' in task.url:
		return None
	return False
