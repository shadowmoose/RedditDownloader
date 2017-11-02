import os
import gzip
import json

# Check manifest was built (should always be during testing).
def run_test(re):
	if not os.path.exists('./download/Manifest.json.gz'):
		return 'Failed to build manifest!', 1
	try:
		with gzip.GzipFile('./download/Manifest.json.gz', 'r') as data_file:
			data = json.load(data_file)
			if '@meta' not in data:
				return 'Manifest missing metadata!', 3
	except Exception as e:
		return ('Failed to extract JSON Manifest: %s' % e), 2
		pass

	return '', 0