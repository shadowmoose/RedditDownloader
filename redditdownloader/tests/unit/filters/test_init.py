import unittest
import filters


class FilterInitTest(unittest.TestCase):
	def setUp(self):
		self.fields = list(filters.filter_fields().keys())

	def test_custom(self):
		""" Make sure custom filters are loading properly """
		self.assertGreater(len(filters.custom_filters()), 0, "Custom filters not loaded!")

	def test_fields(self):
		""" Assure default Filters can be loaded """
		self.assertIsNotNone(self.fields)
		self.assertGreater(len(self.fields), 0)

	def test_default_fields(self):
		""" Assure that all filterable fields are properly loaded as Filters """
		loaded = [f.field for f in filters.get_filters(filter_dict=None)]
		for field in self.fields:
			self.assertIn(field, loaded, "Missing filter for field: %s" % field)

	def test_load(self):
		""" Test loading Filters using the string/dict notation """
		loaded = filters.get_filters(filter_dict={'subreddit.equals': 1})
		self.assertEqual(len(loaded), 1, "Loaded incorrect number of Filters!")

		for f in self.fields:
			for op in filters.Operators:
				fi = filters.get_filters(filter_dict={"%s.%s" % (f, op.value): 1})[0]
				self.assertEqual(fi.operator, op, "Filter %s failed to load with operator %s" % (f, op))
