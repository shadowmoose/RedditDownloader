"""
	Basic module to handle launching the relevant tests from within the script.
"""
import unittest
import os
import sys


application_base = getattr(sys, '_MEIPASS', os.path.abspath(os.path.join(os.path.realpath(__file__), '../../')))
application_path = getattr(sys, '_MEIPASS', os.path.abspath(os.path.join(os.path.realpath(__file__), '../../../')))


def run_tests(test_subdir):
	if '*' in test_subdir or not test_subdir:
		test_subdir = ''  # Run all tests in directory.
	if getattr(sys, 'frozen', False):
		subdir = 'tests/'
	else:
		subdir = 'redditdownloader/tests/'

	test_path = os.path.join(application_path, subdir, test_subdir)
	print("Running tests in %s" % test_path)

	tests = unittest.TestLoader().discover(test_path, top_level_dir=application_base)
	stats = unittest.TextTestRunner(verbosity=2, buffer=True).run(tests)
	return len(stats.failures)
