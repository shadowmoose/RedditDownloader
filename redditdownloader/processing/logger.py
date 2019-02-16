# Logger object to simplify Thread logging.
import threading
import re
from static import stringutil


class Logger:
	def __init__(self, max_lines=3, padding=0):
		self.max_lines = max_lines
		self._lines = [None] * self.max_lines
		self.padding = padding
		self.lock = threading.RLock()
		self.ansi_escape = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -/]*[@-~]')

	def clear(self):
		with self.lock:
			self._lines = [None] * self.max_lines

	def out(self, idx, txt):
		"""
			Set the value of one of this log's lines.
			Clears the sub-values after this line.
		"""
		txt = str(txt)
		with self.lock:
			idx = max(0, min(self.max_lines-1, idx))
			self._lines[idx] = txt.replace('\n', '').strip()
			for i in range(idx+1, self.max_lines):
				self._lines[i] = None

	def raw_lines(self):
		""" Returns an array of the (unpadded) lines in this Log, with ansi characters removed. """
		with self.lock:
			return [self.ansi_escape.sub('', l) if l else None for l in self._lines]

	def render(self, limit=-1, max_width=-1):
		"""
		Convert this log's lines into a complete output string.
		"""
		with self.lock:
			out = ''
			for idx, ln in enumerate(self._lines):
				if ln is None:
					ln = ''
				if 0 <= limit <= idx:
					break
				line = ''
				line += ' ' * ((self.padding+idx)*4)  # 4 spaces per line indent.
				line += ln.strip()
				if 0 < max_width <= len(line)-2:  # !cover
					line = str(line[0:max_width-5])
					line += '...'
				line += stringutil.Style.RESET_ALL + '\n'
				out += line
			return out


if __name__ == '__main__':
	lo = Logger()
	for ind in range(3):
		lo.out(ind, "Number %s" % ind)
	print('Full')
	print(lo.render())
	print('Fewer lines:')
	print(lo.render(2))
	lo.out(1, "new subtext")
	print("Changed.")
	print(lo.render())

	print(lo.render(-1, 15))
