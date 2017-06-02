def run_test(re):
	if not re.me or not re.me.name or 'test_' not in re.me.name:
		return 'Invalid username!', 1;
	return '', 0;