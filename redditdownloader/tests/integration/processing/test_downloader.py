import static.settings as settings
import sql
from tests.mock import EnvironmentTest
from processing import downloader
import importlib
from processing.wrappers import QueueReader
import multiprocessing
from threading import Thread
import time
import queue


class DownloaderTest(EnvironmentTest):
	env = 'rmd_staged_db'

	def setUp(self):
		importlib.reload(settings)
		importlib.reload(sql)
		settings.load(self.settings_file)
		settings.put('output.base_dir', self.dir)
		sql.init_from_settings()

	def tearDown(self):
		sql.close()

	def test_download(self):
		""" Downloader should work """
		stop_event = multiprocessing.Event()
		in_queue = multiprocessing.Queue()
		ack_queue = multiprocessing.Queue()
		reader = QueueReader(in_queue, stop_event)
		dl = downloader.Downloader(reader, ack_queue, settings.to_json(), multiprocessing.RLock())
		stats = {'ack': 0, 'sent': 0}

		def add_test(inf):
			sess = sql.session()
			lst = sess.query(sql.URL).all()
			st = time.time()
			sent = []
			for l in lst:
				in_queue.put_nowait(l.id)
				inf['sent'] += 1
				sent.append(l.id)
			while time.time() - st < 30 and sent:
				try:
					rd = ack_queue.get(block=True, timeout=.5)
					inf['ack'] += 1
					sent.remove(rd.url_id)
				except queue.Empty:
					pass
			sess.close()
			stop_event.set()

		thread = Thread(target=add_test, args=(stats,))
		thread.start()
		dl.run()
		thread.join()
		self.assertGreater(stats['sent'], 0, msg='Failed to send any test URLS for download!')
		self.assertEqual(stats['sent'], stats['ack'], msg='Not all sent URLs were Acked!')
		self.assertFalse(dl.progress.get_running(), msg='Failed to clear running status!')
