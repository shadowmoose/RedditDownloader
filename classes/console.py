"""
	Package for getting & validating user input in various ways, via the console.
"""
import stringutil
from stringutil import Fore


def col_input(prompt, color=Fore.LIGHTYELLOW_EX):
	""" Prints a colorized input prompt. """
	stringutil.print_color(color, prompt, end='')
	return input()


def number(prompt, min_num = None, max_num = None, round_val=True):
	"""
	Prompts the user for a number.
	:param prompt: The string to display
	:param min_num: The minimum value to accept.
	:param max_num: The amximum value to accept.
	:param round_val: If the value should be rounded.
	:return: The value chosen, or none.
	"""
	while True:
		text = col_input("%s: " % prompt)
		if not stringutil.is_numeric(text):
			continue
		num = float(text)
		if round_val:
			num = int(round(num, 0))
		if min_num is not None and num < min_num:
			continue
		if max_num is not None and num > max_num:
			continue
		return num


def prompt_list(prompt, options, allow_none=False):
	""" Prompts for the user to select an option from the list, and returns the index.
	 	If *options* is an array of tuples, they are prompted with [0], and [1] is returned.
	"""
	if len(options) == 0:
		return None
	stringutil.print_color(Fore.CYAN, prompt)
	is_tuple = isinstance(options[0], tuple)
	if not is_tuple:
		options = [(o, o) for o in options]
	if allow_none:
		options.append(('Cancel', None))
	for idx, opt in enumerate(options):
		print("\t%s: %s" % (idx+1, opt[0]) )
	select = number("Choose an option", 1, len(options), round_val=True) - 1
	return options[select][1]


def confirm(prompt, default=None):
	""" Prompts the user with a confirmation dialogue, supporting optional default. """
	defa = '[y]/n'
	if default is None:
		defa = 'y/n'
	elif not default:
		defa = 'y/[n]'
	inp = col_input("%s(%s): " % (prompt, defa))
	if inp=='' and default is not None:
		return default
	return 'y' in inp.lower()


def string(prompt, auto_strip=True):
	""" Prompts the user, just like *col_input()*, but returns None if nothing was input. """
	ret = col_input("%s: " % prompt)
	if auto_strip:
		ret = ret.strip()
	if ret=='':
		return None
	return ret


def pause():
	""" Prompts the User to press any button to continue. """
	stringutil.print_color(Fore.GREEN, '[Press Enter to continue]')
	input()


if __name__ == '__main__':
	print(prompt_list('Test non-tuple:', ['one', 'two', 'three'], allow_none=True))
	ans = prompt_list('Available Modules:', [('Module one', 'one'),('Module two', 'two'),('Module three', 'three')])
	print("Chose: %s" % ans)

	print(confirm("Everything look good?", True))
	print(confirm("No default confirmation: ", None))