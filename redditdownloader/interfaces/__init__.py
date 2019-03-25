from abc import ABC, abstractmethod


class UserInterface(ABC):

	def __init__(self, ui_id, rmd_version):
		self.ui_id = ui_id
		self.rmd_version = rmd_version

	@abstractmethod
	def display(self):
		"""
		The primary method to implement, this is called when this UI should take over rendering.

		Calling this does not *require* that RMD starts downloading at once,
		however, this UI should facilitate that functionaliy.
		"""
		pass
