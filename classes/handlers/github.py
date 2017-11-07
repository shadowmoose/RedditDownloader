tag = 'github'
order = 2

# Return filename/directory name of created file(s), False if a failure is reached, or None if there was no issue, but there are no files.
def handle(url, data):
	if 'github.com' in url:
		return None;
	return False;