import tools.ffmpeg_download as ffmpeg
from tests.mock import StagedTest
import os
import subprocess


class FFmpegDownloadTest(StagedTest):
	def test_local_install(self):
		""" Download ffmpeg into the mock local directory """
		file = ffmpeg.install_local(local_dir=self.dir, verbose=False, force_download=True)
		self.assertTrue(file, msg='FFmpeg was not downloaded!')
		self.assertIn('ffmpeg', file, msg='FFmpeg filename was invalid!')
		self.assertTrue(os.path.exists(file), msg='FFmpeg binary does not exist!')
		output = subprocess.check_output([file, '-version']).decode('utf-8')
		self.assertIn('ffmpeg version', output, msg='Failed to execute ffmpeg version check!')
