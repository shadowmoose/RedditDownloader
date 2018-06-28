import os
from classes.static import manifest

# Check manifest was built (should always be during testing).


def run_test(re):
	if not os.path.exists('manifest.sqldb'):
		return 'Failed to build manifest!', 1  # !cover
	# noinspection PyProtectedMember
	_c = manifest._expose_testing_cursor()
	_c.execute('SELECT post_id, file_path FROM urls')
	_failed = 0
	_invalid = 0
	_total = 0
	for r in _c.fetchall():
		_pid = r[0]
		_file = r[1]
		_total += 1
		if _file == 'None' or _file == 'False':
			_failed += 1
			continue
		if not os.path.exists(_file):
			print(_pid, _file)
			_invalid += 1
	if _total != 5:
		return 'Incorrect number of entries in Manifest.', 2
	if _invalid > 0:
		return 'Manifest contains invalid file paths.', 3
	if _failed > 0:
		return 'Manifest contains failed URLs.', 4

	return '', 0
