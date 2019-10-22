import unittest
from static import stringutil as su


class StringUtilTest(unittest.TestCase):
	def test_error(self):
		""" Error coloring should print """
		su.error('test error')

	def test_html_elements(self):
		""" All HTML elements should be found """
		html = '''<afake href="nope"></fake><a href="test"><a href="test-nested"></a></a>'''
		self.assertEqual(sorted(su.html_elements(html)), sorted(['test', 'test-nested']))

	def test_is_numeric(self):
		""" Numeric strings should be identified """
		self.assertTrue(su.is_numeric('10.1'), msg="Failed to ID '10.1'!")
		self.assertTrue(su.is_numeric(-100), msg="Failed to ID -100!")
		self.assertTrue(su.is_numeric('-1337'), msg="Failed to ID '-1337'!")
		self.assertFalse(su.is_numeric('-1337-'), msg="Improperly cast '-1337-'!")
		self.assertFalse(su.is_numeric('abc'), msg="Improperly cast 'abc'!")
		self.assertFalse(su.is_numeric('--1'), msg="Improperly cast '--1'!")

	def test_print_color(self):
		""" All colors should print without throwing """
		for c in su._special_colors.keys():
			su.print_color(c, 'Test Color Print %s' % c)
