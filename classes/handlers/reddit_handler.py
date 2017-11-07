tag = 'reddit'
order = 2

# Return filename/directory name of created file(s), False if a failure is reached, or None if there was no issue, but there are no files.
def handle(url, data):
	if 'reddit.com' in url or url.strip().startswith('/r/'):
		return None;
	return False;