import os;

# Check manifest was built (should always be during testing).
def run_test(re):
	if not os.path.exists(re.manifest_file):
		return 'Failed to build manifest!', 1;
	return '', 0;