import static.settings as settings
from tests.mock import EnvironmentTest
from sources import UpvotedSaved
import os
import importlib


class SettingsTest(EnvironmentTest):
	env = 'rmd_1.0_settings'

	def setUp(self):
		importlib.reload(settings)
		settings.load(self.settings_file)

	def tearDown(self):
		importlib.reload(settings)

	def test_load_old(self):
		""" Settings from v1 should load """
		self.assertEqual(settings.get('auth.refresh_token'), "", msg="Refresh key was incorrectly loaded!")
		self.assertNotEqual(settings.get('auth.rmd_client_key'), '', msg='Failed to set default RMD client key!')
		self.assertTrue(os.path.isabs(settings.get('output.base_dir')), msg='Legacy download dir was not converted!')

	def test_get(self):
		""" get() method should work """
		self.assertEqual(settings.get('auth.refresh_token'), "", msg='Failed to get() correct value!')
		with self.assertRaises(KeyError, msg='Failed to raise on invalid key!'):
			settings.get('fake.key')

	def test_put(self):
		""" Put should work as expected """
		settings.put('auth.oauth_key', 'value')
		self.assertEqual(settings.get('oauth_key', cat='auth'), 'value', msg='Failed to set correct value!')

		with self.assertRaises(TypeError, msg="Failed to catch invalid value!"):
			settings.put('interface.start_server', 'invalid')

	def test_get_all(self):
		""" All settings should be accounted for """
		self.assertEqual(21, len(list(settings.get_all())), msg='Got invalid amount of settings!')

	def test_sources(self):
		""" Getting/Add/Remove Sources should work """
		srcs = settings.get_sources()
		cnt = len(srcs)
		self.assertGreater(cnt, 0, msg='Failed to get any sources!')
		settings.add_source(srcs[0], prevent_duplicate=True)
		self.assertEqual(len(settings.get_sources()), cnt, msg='Incorrectly added duplicate source!')

		ups = UpvotedSaved()
		ups.set_alias('new-source')
		settings.add_source(ups)
		self.assertGreater(len(settings.get_sources()), cnt, msg='Failed to add new source!')

		settings.remove_source(ups)
		self.assertEqual(cnt, len(settings.get_sources()), msg='Failed to remove source!')

	def test_to_obj(self):
		""" Removing sources should work """
		ob = settings.to_obj(save_format=False, include_private=True)
		for s in settings.get_all():
			self.assertIn(s.category, ob, msg='Category "%s" is missing from Object!' % s.category)
			found = [cs for cs in ob[s.category] if cs['name'] == s.name]
			self.assertTrue(found, msg='Setting "%s" is missing from Object!' % s.name)

	def test_conversion(self):
		""" Settings should cast values correctly """
		s = settings.get('interface.port', full_obj=True)
		s.set(10)
		self.assertEqual(s.val(), 10, msg='Setting set() failed!')
		s.set('1337.1')
		self.assertEqual(s.val(), 1337, msg='Setting set() string->int failed!')

		s = settings.get('interface.start_server', full_obj=True)
		s.set('Yes')
		self.assertTrue(s.val(), msg='Failed to cast boolean True from "Yes".')
		s.set('n')
		self.assertFalse(s.val(), msg='Failed to cast boolean True from "n".')
		s.set(1)
		self.assertTrue(s.val(), msg='Failed to cast boolean True from 1.')
		with self.assertRaises(TypeError, msg='Failed to catch Type error!'):
			s.set('fake')

	def test_saving(self):
		""" Saving should work """
		os.unlink(self.settings_file)
		self.assertTrue(settings.save(), msg="Save failed!")
		self.assertTrue(os.path.isfile(self.settings_file), msg='Failed to rebuild Settings file on save!')
		settings.disable_saving()
		self.assertFalse(settings.save(), msg="Settings saved after disabling!")
