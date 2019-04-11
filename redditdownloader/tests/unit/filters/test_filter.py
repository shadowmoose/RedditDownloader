import unittest
import filters
import json
from filters.filter import Filter
from filters.url_match_filter import URLFilter
from filters.created_utc_filter import UTCFilter
from tests.mock import Object


class FilterTest(unittest.TestCase):
	def setUp(self):
		self.filter = Filter("field", "description")
		self.ops = [op.value for op in filters.Operators]

	def test_operator(self):
		""" Setting & validating Operators"""
		for op in self.ops:
			self.filter.set_operator(op)
			self.assertEqual(self.filter.operator.value, op)

	def test_limit(self):
		""" Filters should auto-cast limits to int """
		for lim in [1, '234', -100, '-200']:
			self.filter.set_limit(lim)
			self.assertEqual(int(lim), self.filter.get_limit(), "Limit mismatch: %s!=%s" % (lim, self.filter.get_limit()))
		self.filter.set_limit('test')
		self.assertEqual('test', self.filter.get_limit(), "String set failed for Filter limit.")

	def test_desc(self):
		""" Filter should always have description """
		self.assertEqual('description', self.filter.get_description())

	def test_check(self):
		""" Always compare string & numeric via casting """
		self.filter.set_operator('.equals')
		for lim in [10, '10']:
			self.filter.set_limit(lim)
			for val in [10, '10']:
				ob = Object(field=val)
				self.assertTrue(self.filter.check(ob), "Failed Filter comparison check - Fields should match!")

	def test_check_match(self):
		""" Regex pattern matching """
		self.filter.set_operator('.match')  # Regex check
		self.filter.set_limit('te*')
		for val in ['test 1', 'test_2', '3_test']:
			self.assertTrue(self.filter.check(Object(field=val)))
		self.assertFalse(self.filter.check(Object(field="fail")))

	def test_check_max(self):
		""" Max should compare properly """
		self.filter.set_operator(".max")
		self.filter.set_limit(12)
		self.assertTrue(self.filter.check(Object(field=12)))
		self.assertTrue(self.filter.check(Object(field=0)))
		self.assertFalse(self.filter.check(Object(field=13)))

	def test_check_min(self):
		""" Min should compare properly """
		self.filter.set_operator(".min")
		self.filter.set_limit(12)
		self.assertTrue(self.filter.check(Object(field=12)))
		self.assertTrue(self.filter.check(Object(field=15)))
		self.assertFalse(self.filter.check(Object(field=9)))

	def test_obj(self):
		""" Filters to_keyval() & from_keyval() should work with any Operator """
		for op in self.ops:
			self.filter.set_limit('1')
			self.filter.set_operator(op)
			key, val = self.filter.to_keyval()
			obj = Filter(self.filter.field, 'test')
			self.assertTrue(obj.from_keyval(key, val), 'Unable to convert filter from key/val.')
			self.assertEqual(obj.field, self.filter.field, 'Converted Filter field was not equal to original.')
			self.assertEqual(self.filter.get_limit(), obj.get_limit(), 'Converted Filter limit was not equal.')
			self.assertEqual(self.filter.operator, obj.operator, 'Converted FIlter Operator was not equal.')

	def test_json(self):
		""" Should be JSON encodable """
		self.assertIsNotNone(json.loads(json.dumps(self.filter.to_js_obj())), "JSON conversion failed!")

	def test_str(self):
		""" Make sure string output works """
		self.filter.set_operator('.match')
		self.filter.set_limit("test")
		self.assertTrue(str(self.filter), "String conversion failed!")

	def test_utc(self):
		""" UTCFIlter should compare properly """
		utc = UTCFilter()
		utc.set_limit(1000)
		utc.set_operator('.max')
		self.assertTrue(utc.check(Object(created_utc=1)))

	def test_url_pattern(self):
		""" URLFIlter should compare properly """
		url = URLFilter()
		url.set_limit("goog*")
		self.assertTrue(url.check(Object(get_urls=lambda: ['google.com'])))

