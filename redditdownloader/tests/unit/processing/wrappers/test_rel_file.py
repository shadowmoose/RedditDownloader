import unittest
import processing.wrappers.rel_file as rel


class RelFileTest(unittest.TestCase):
	def test_rel(self):
		rf = rel.SanitizedRelFile(base="C:/Users", file_path="t/./test/[title].txt")
		self.assertEqual("C:/Users/t/test/[title].txt", rf.absolute(), 'Invalid absolute path!')
		self.assertEqual('t/test/[title].txt', rf.relative(), 'Invalid relative path!')

	def test_invalid(self):
		""" Validate that relative files cannot break above their established Base. """
		with self.assertRaises(rel.RelError):
			rel.SanitizedRelFile(base='C://Users', file_path='t/../../nope.txt')

	def test_pre_strip(self):
		self.assertEqual('C:/Users/nope.txt', rel.SanitizedRelFile(base='C://Users', file_path='../nope.txt').absolute())

	def test_relative(self):
		r = rel.SanitizedRelFile('./base', '../../1/2/file.txt')
		self.assertEqual('1/2/file.txt', r.relative())

	def test_sanitize(self):
		r = rel.SanitizedRelFile("C:\\Fake\\", './test\\!@#$%^&*()_+-=.../...\\1234567890abcd...file..')
		self.assertEqual(r.relative(), 'test/!@#$%^&_()_+-=/1234567890abcd...file', 'The crazy (valid) file failed!')
