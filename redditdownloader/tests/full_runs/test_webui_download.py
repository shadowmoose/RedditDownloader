import static.settings as settings
from tests.mock import EnvironmentTest
from interfaces.eelwrapper import WebUI
from os.path import join
import sql
import requests
from threading import Thread
import unittest


download_ran = False
session = None
thread = None


@unittest.skip("Not ready to test yet.")
class WebUIDownloadTest(EnvironmentTest):
	env = 'controlled_sources'

	def setUp(self):
		global download_ran, session, thread
		if not download_ran:
			download_ran = True
			self.wui = WebUI('test_version')
			self.db_path = join(settings.get('output.base_dir'), 'manifest.sqlite')
			self.url = 'http://%s:%s/index.html#' % (settings.get('interface.host'), settings.get('interface.port'))

			settings.load(self.settings_file)
			settings.put('interface.start_server', True)
			sql.init_from_settings()
			session = sql.session()
			thread = Thread(target=self.wui.display)
			thread.setDaemon(True)
			thread.start()
			self.assertTrue(self.wui.waitFor(10), msg='WebUI Failed to start!')

	def test_ui_running(self):
		resp = requests.get(self.url)
		self.assertTrue(resp.text)
