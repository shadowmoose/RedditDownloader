import os;

# Check manifest was built (should always be during testing).
def run_test(re):
	if not os.path.exists('./download/Manifest.json'):
		return 'Failed to build manifest!', 1;
	return '', 0;