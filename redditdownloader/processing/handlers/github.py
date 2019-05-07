from processing.handlers import HandlerResponse

tag = 'github'
order = 1


def handle(task, progress):  # !cover
	if 'github.com' in task.url:
		return HandlerResponse(success=False, handler=tag, failure_reason="Github links are disabled.")
	return False
