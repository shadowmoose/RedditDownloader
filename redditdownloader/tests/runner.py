"""
	Basic module to handle launching the relevant tests from within the script.
"""
import unittest
import os


def run_tests(test_subdir):
	if '*' in test_subdir:
		test_subdir = ''  # Run all tests in directory.
	print("Running %s tests" % (test_subdir if test_subdir else 'all'))
	base_dir = os.path.dirname(os.path.realpath(__file__))
	tests = unittest.TestLoader().discover('redditdownloader/tests/'+test_subdir, top_level_dir=base_dir)
	stats = unittest.TextTestRunner(verbosity=1).run(tests)
	return len(stats.failures)
