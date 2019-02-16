import threading


'''
	This class was found online, and it's great! 
	It gives locking priority to writers, and allows concurrent readers.
	I've slightly modified it to support an __enter__ and __exit__ method, for convenience.
	See the bottom of this file for examples using it.
	
	NOTE: This is NOT a Reentrant Lock! Lock with this only at the deepest reasonable levels to avoid hanging.
	
	See the original (?) here: http://code.activestate.com/recipes/577803-reader-writer-lock-with-priority-for-writers/
	
	Please be nice, and make sure the original author gets their credit.
	Enjoy, 
		ShadowMoose
'''

__author__ = "Mateusz Kobos"


class RWLock:
	"""Synchronization object used in a solution of so-called second
	readers-writers problem. In this problem, many readers can simultaneously
	access a share, and a writer has an exclusive access to this share.
	Additionally, the following constraints should be met:
	1) no reader should be kept waiting if the share is currently opened for
		reading unless a writer is also waiting for the share,
	2) no writer should be kept waiting for the share longer than absolutely
		necessary.
	The implementation is based on [1, secs. 4.2.2, 4.2.6, 4.2.7]
	with a modification -- adding an additional lock (C{self.__readers_queue})
	-- in accordance with [2].
	Sources:
	[1] A.B. Downey: "The little book of semaphores", Version 2.1.5, 2008
	[2] P.J. Courtois, F. Heymans, D.L. Parnas:
		"Concurrent Control with 'Readers' and 'Writers'",
		Communications of the ACM, 1971 (via [3])
	[3] http://en.wikipedia.org/wiki/Readers-writers_problem
	"""

	def __init__(self):
		self.__read_switch = _LightSwitch()
		self.__write_switch = _LightSwitch()
		self.__no_readers = threading.Lock()
		self.__no_writers = threading.Lock()
		self.__readers_queue = threading.Lock()
		"""A lock giving an even higher priority to the writer in certain
		cases (see [2] for a discussion)"""

	def reader_acquire(self):
		self.__readers_queue.acquire()
		self.__no_readers.acquire()
		self.__read_switch.acquire(self.__no_writers)
		self.__no_readers.release()
		self.__readers_queue.release()

	def reader_release(self):
		self.__read_switch.release(self.__no_writers)

	def writer_acquire(self):
		self.__write_switch.acquire(self.__no_readers)
		self.__no_writers.acquire()

	def writer_release(self):
		self.__no_writers.release()
		self.__write_switch.release(self.__no_readers)

	def __call__(self, a_type):
		""" This lock secretly hands out private objects that can handle __enter__ and __exit__ for it. """
		return _Lockr(self, a_type)


class _LightSwitch:
	"""An auxiliary "light switch"-like object. The first thread turns on the
	"switch", the last one turns it off (see [1, sec. 4.2.2] for details)."""
	def __init__(self):
		self.__counter = 0
		self.__mutex = threading.Lock()

	def acquire(self, lock):
		self.__mutex.acquire()
		self.__counter += 1
		if self.__counter == 1:
			lock.acquire()
		self.__mutex.release()

	def release(self, lock):
		self.__mutex.acquire()
		self.__counter -= 1
		if self.__counter == 0:
			lock.release()
		self.__mutex.release()


class _Lockr:
	def __init__(self, targ_lock, a_type):
		self.lock = targ_lock
		self.type = 'w' if 'w' in a_type.lower() else 'r'

	def __enter__(self):
		if 'r' in self.type:
			# print('+Obtaining reader lock [%s].' % id(self))
			self.lock.reader_acquire()
			return self
		if 'w' in self.type:
			# print('-Obtaining writer lock [%s].' % id(self))
			self.lock.writer_acquire()
			return self
		raise Exception('Bad lock type.')

	def __exit__(self, exc_type, exc_val, exc_tb):
		if self.type == 'r':
			self.lock.reader_release()
		if self.type == 'w':
			self.lock.writer_release()
		# print('!Released "%s" lock [%s].' % (self.type, id(self)))


if __name__ == '__main__':
	print('Testing RWLock.\n')
	rwl = RWLock()

	with rwl('r'):
		print('\tRead lock acquired!')
		with rwl('r'):
			print('\t\t+Multiple concurrent readers confirmed as OK.')

	with rwl('w'):
		print('\tWrite lock acquired!')
		print('SHOULD PERMA-FREEZE NOW:')
		with rwl('r'):
			raise Exception('Writer didn\'t lock readers out properly!')  # This should never happen if it's working.
		with rwl('w'):
			raise Exception('Writer didn\'t lock other writers out properly!')  # This can never happen, but here it is.
