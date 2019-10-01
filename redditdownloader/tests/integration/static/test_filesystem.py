import static.filesystem as fs
from tests.mock import StagedTest
import os
from os.path import join, isdir, isfile, isabs


class FileSystemTest(StagedTest):
	def test_find_file(self):
		""" Finding local or user-dir files should work """
		fname = 'rmd-test-find-file.test'
		external = fs.find_file(fname)
		self.assertIsNotNone(external, msg='Failed to generate a user-dir file path.')
		with open(fname, 'a'):
			pass
		local = fs.find_file(fname)
		os.unlink(fname)
		self.assertNotEqual(external, local, msg='Failed to locate different local & external files.')
		self.assertTrue(isabs(local), 'Local file is not absolute path.')
		self.assertTrue(isabs(external), 'User-dir file is not absolute path.')

	def test_mkpath(self):
		""" Making paths should work """
		basepath = join(self.dir, 'test', 'test2')
		pth = join(basepath, 'file.ext')
		fs.mkpath(pth)
		self.assertTrue(isdir(basepath), msg='Failed to create the parent directories with mkpath.')
		self.assertFalse(isfile(pth), msg='Test file was incorrectly created by mkpath.')

	def test_copen(self):
		""" The copen method should work """
		subdir = join(self.dir, 'subdir')
		pth = join(subdir, 'test.txt')
		with fs.copen(pth, 'a', autofind=False) as o:
			o.write('test')
		self.assertTrue(isfile(pth), 'Failed to write to file using cout')
		self.assertTrue(isdir(subdir), 'Failed to generate correct subdirectory')

	def test_is_subpath(self):
		""" Detecting subpaths should always work """
		self.assertTrue(fs.is_subpath('/test/sub/path', '/test/sub/path/file.txt'), msg='Incorrectly judged basic subpath')
		self.assertFalse(fs.is_subpath('/test/sub/path', '/test/sub/test.txt'), msg='Wrongly found basic non-subpath')
		self.assertFalse(fs.is_subpath('/test/path/', '/test/path/subdir/../../../nope'), msg='Invalid escalation in path')
		self.assertTrue(fs.is_subpath('/test/subpath', '/test/subpath'), msg='Missed matching subpaths.')

	def test_r_unlink(self):
		""" Unlink should prune parent dirs """
		basepath = join(self.dir, 'test', 'test2')
		pth = join(basepath, 'file.ext')
		with open(join(self.dir, 'basefile.txt'), 'w') as o:
			o.write('test')
		with fs.copen(pth, 'w') as o:
			o.write('test2')
		self.assertTrue(isfile(pth), 'Test file was not created.')
		fs.r_unlink(pth)
		self.assertFalse(isfile(pth), 'Test file was not deleted.')
		self.assertFalse(isdir(basepath), 'Parent path was not cleaned up after file removal.')
		self.assertTrue(isdir(self.dir), 'Base directory was removed by pruning.')

	def test_writable(self):
		""" The use file dir should be writable """
		pth = fs.find_file('test-fake-rmd-file.test')
		with fs.copen(pth, 'w') as o:
			o.write('test')
		self.assertTrue(isfile(pth), msg='Failed to write file!')
		os.unlink(pth)
		self.assertFalse(isfile(pth), msg='Failed to clean up file!')
