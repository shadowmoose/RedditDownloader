import unittest
import processing.wrappers.rel_file as rel
from os.path import abspath


class RelFileTest(unittest.TestCase):
	def test_rel(self):
		""" Paths should be collapsed """
		rf = rel.SanitizedRelFile(base="/Users/./", file_path="t/./test/[title].txt")
		self.assertEqual(norm("/Users/t/test/[title].txt"), rf.absolute(), 'Invalid absolute path!')
		self.assertEqual('t/test/[title].txt', rf.relative(), 'Invalid relative path!')

	def test_invalid(self):
		""" Files cannot escalate above their Base """
		with self.assertRaises(rel.RelError, msg="Failed to catch dangerous file escalation!"):
			rel.SanitizedRelFile(base='C://Users', file_path='t/../../nope.txt')
		self.assertEqual('_', rel.SanitizedRelFile(base='C://Users', file_path=' \t\n ../ ./ . \\ ').relative())

	def test_path_concat(self):
		""" Leading directory dots should be stripped in full paths """
		self.assertEqual(norm('/Users/nope.txt'), rel.SanitizedRelFile(base='/Users', file_path='../nope.txt').absolute())

	def test_relative(self):
		""" Relative files should not include path prefixes """
		r = rel.SanitizedRelFile('./base', '../../1/2/file.txt')
		self.assertEqual('1/2/file.txt', r.relative())

	def test_sanitize(self):
		""" Certain special characters should be stripped """
		r = rel.SanitizedRelFile("/Fake\\", './test\\!@#$%^&*()_+-=.../...\\.1234567890abcd...file..')
		self.assertEqual(r.relative(), 'test/!@#$%^&_()_+-=/1234567890abcd...file', 'The crazy (valid) file failed!')

	def test_hash_path(self):
		""" Hashed paths should reliably work """
		r = rel.SanitizedRelFile(base="/Users", file_path="/test/[title].txt")
		self.assertTrue(r.abs_hashed(), msg='abs_hashed() returned an invalid value!')


def norm(fn):
	return abspath(fn).replace('\\', '/')
