from processing.handlers import HandlerResponse

tag = 'reddit'
order = 1


def handle(task, progress):  # !cover
	if 'reddit.com' in task.url or any(task.url.strip().startswith(p) for p in ['/r/', '/u/']):
		return HandlerResponse(success=False, handler=tag, failure_reason="Reddit links are disabled.")
	return False
