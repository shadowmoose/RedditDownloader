import os
import gzip
import json

# Check manifest was built (should always be during testing).
def run_test(re):
	if not os.path.exists('./download/manifest.sqldb'):
		return 'Failed to build manifest!', 1 #!cover

	return '', 0