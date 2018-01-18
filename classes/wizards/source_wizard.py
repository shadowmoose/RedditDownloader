"""
	Wizard for handling Source editing.
"""

import console
import stringutil as su
import wizards.wizard_functions as wizard_functions

class SourceEditor:
	def __init__(self, source, settings):
		self.source = source
		self.settings = settings

	def run(self):
		""" The editor screen for a specific Source. """
		while True:
			print('\n\n\n')
			su.print_color(su.Fore.GREEN, 'Editing Source: "%s" -> %s' % (self.source.get_alias(), self.source.get_config_summary()) )
			filters = self.source.get_filters()
			if len(filters) > 0:
				for f in filters:
					print('\t-%s' % f)

			choice = console.prompt_list('What would you like to do with this Source?',[
				('Edit this Source', 'edit'),
				('Rename', 'rename'),
				('Delete this Source', 'delete'),
				('Add a Filter', 'add_filter'),
				('Remove a Filter', 'remove_filter'),
				('Nothing', 'exit')
			])
			print('\n')

			if choice == 'edit':
				self._edit_source()

			if choice == 'rename':
				self._rename()

			if choice == 'delete':
				self._delete()

			if choice == 'add_filter':
				self._add_filter()

			if choice == 'remove_filter':
				self._remove_filter()

			if choice == 'exit':
				break


	def _edit_source(self):
		if self.source.setup_wizard():
			wizard_functions.save_source(self.settings, self.source)
		else:
			print('Edit failed.')


	def _rename(self):
		name = wizard_functions.get_unique_alias(self.settings)
		if name is None:
			return
		self.settings.remove_source(self.source)
		self.source.set_alias(name)
		self.settings.add_source(self.source)
		print('Renamed Source.')


	def _delete(self):
		if console.confirm('Are you sure you want to delete this Source?', default=False):
			self.settings.remove_source(self.source)
			print('Source deleted.')
			return
		else:
			print('Source not removed.')


	def _add_filter(self):
		from filters import filter
		print('To create a filter, select the field to filter by, how it should be compared, '
			  'and then the value to compare against.')
		new_filter = console.prompt_list(
			"What do you want to filter this source's Posts by?",
			[("%s" % fi.get_description(), fi) for fi in filter.get_filters()],
			allow_none=True
		)
		if new_filter is None:
			print('Not adding Filter.')
			return
		if new_filter.accepts_operator:
			comp = console.prompt_list(
				'How should we compare this field to the value you set?',
				[(fv.value.replace('.', ''), fv) for fv in filter.Operators]
			)
			new_filter.set_operator(comp)
		limit = console.string('Value to compare to', auto_strip=False)
		if limit is None:
			print('Aborted filter setup.')
			return
		new_filter.set_limit(limit)
		self.source.add_filter(new_filter)
		wizard_functions.save_source(self.settings, self.source)


	def _remove_filter(self):
		filters = self.source.get_filters()
		if len(filters) == 0:
			print('No Filters to remove.')
			return
		rem = console.prompt_list(
			'Select a Filter to remove:',
			[(str(fi), fi) for fi in filters],
			allow_none=True
		)
		if rem is None:
			print("Removing nothing.")
			return
		self.source.remove_filter(rem)
		wizard_functions.save_source(self.settings, self.source)