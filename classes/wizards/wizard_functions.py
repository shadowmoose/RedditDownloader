"""
	A few functions for all Wizards, packaged.
"""
import console

def get_unique_alias(settings):
	""" Prompts the user for a unique Source Alias, or None if they cancel. """
	while True:
		name = console.string("Choose a unique, descriptive name for this Source")
		if name is None:
			return None
		if settings.has_source_alias(name):
			print('A source with that name already exists. It must be unique!')
			continue
		return name


def save_source(settings, source):
	""" Shuffle the source to re-write changes to file. """
	settings.remove_source(source)
	settings.add_source(source)