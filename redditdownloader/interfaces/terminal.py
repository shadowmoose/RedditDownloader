from interfaces import UserInterface
from processing.controller import RMDController
from static import settings
import colorama
import os


class TerminalUI(UserInterface):
	def __init__(self):
		super().__init__(ui_id="terminal")

	def display(self):
		controller = RMDController()
		controller.start()
		prog = controller.get_progress()

		while controller.is_alive():
			self.print_info(prog)
			if not controller.wait_refresh_rate():
				controller.join()
				break
		print("All finished.")

	def print_info(self, prog):
		if not settings.get('threading.console_clear_screen'):
			print('\n'*10)
		else:
			try:
				print(colorama.ansi.clear_screen())
			except AttributeError:
				os.system('cls' if os.name == 'nt' else 'clear')
		scanning = '+' if prog.loader.get_scanning() else ''
		print("Remaining: %s/%s%s" % (prog.loader.get_queue_size(), prog.loader.get_found(), scanning))
		rj = 10
		for progress in prog.downloaders:
			print()
			print('File:', progress.get_file())
			print('Handler:'.rjust(rj), progress.get_handler())
			print('Status:'.rjust(rj), progress.get_status())
			if progress.get_percent():
				print('Percent:'.rjust(rj), '%s%%' % progress.get_percent())
			else:
				print()
