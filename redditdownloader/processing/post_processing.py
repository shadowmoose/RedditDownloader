import multiprocessing
import traceback
import hashlib
from PIL import Image
import sql
from static import settings
from processing.wrappers import SanitizedRelFile, DownloaderProgress
from sql import File, URL
from sqlalchemy.orm import joinedload

# TODO: Once the stop_event is set, use the reader() class to submit filenames to the downloader threads, to split the Hashing job up.


class Deduplicator(multiprocessing.Process):
	def __init__(self, settings_json, stop_event):
		"""
		Create a Hasher Process, which will be bound to the stop_event, performing post-processing on downloaded Files.
		"""
		super().__init__()
		self._settings = settings_json
		self._stop_event = stop_event
		self.progress = DownloaderProgress()
		self.progress.clear(status="Starting up...")
		self._session = None
		self.daemon = True

	def run(self):
		""" Threaded loading of elements. """
		settings.from_json(self._settings)
		sql.init_from_settings()
		try:
			self._session = sql.session()
			self.progress.clear(status="Starting up...")
			self.progress.set_running(True)

			while not self._stop_event.is_set():
				self._dedupe()
				self.progress.set_status("Waiting for new files...")
				self._stop_event.wait(2)
			self._dedupe()  # Run one final pass after downloading stops.
			self.progress.clear(status="Finished.", running=False)
		except Exception as ex:
			print('Deduplication Process Error:', ex)
			self.progress.set_error(ex)
			self.progress.set_running(False)
			traceback.print_exc()
		finally:
			sql.close()

	def _dedupe(self):
		unfinished = self._session\
			.query(File) \
			.options(joinedload(File.urls))\
			.filter(File.hash == None)\
			.filter(File.downloaded == True)\
			.all()

		unfinished = list(filter(lambda _f: not any(u.album_id for u in _f.urls), unfinished))  # Filter out albums.

		if not unfinished:
			return

		for idx, f in enumerate(unfinished):
			self.progress.set_status("Deduplicating (%s) files..." % (len(unfinished) - idx))
			path = SanitizedRelFile(base=settings.get("output.base_dir"), file_path=f.path)
			is_album = any(u.album_id for u in f.urls)
			if not path.is_file() or is_album:
				continue
			new_hash = FileHasher.get_best_hash(path.absolute())
			# print('New hash for File:', f.id, '::', new_hash)
			matches = [] if is_album else self._find_matching_files(new_hash, ignore_id=f.id)
			f.hash = new_hash
			if len(matches):
				print("Found duplicate files: ", new_hash, "::", [(m.id, m.path) for m in matches])
				best, others = self._choose_best_file(matches + [f])
				print('Chose best File:', best.id)
				for o in others:
					self._upgrade_file(new_file=best, old_file=o)
			self._session.commit()
		self._prune()

	def _find_matching_files(self, search_hash, ignore_id):
		all_hashes = self._session \
			.query(File) \
			.options(joinedload(File.urls)) \
			.filter(File.hash != None) \
			.filter(File.downloaded == True) \
			.filter(File.id != ignore_id) \
			.all()
		matches = []
		for pm in all_hashes:
			if any(u.album_id for u in pm.urls) or any(not u.processed for u in pm.urls):
				continue
			if FileHasher.hamming_distance(search_hash, pm.hash) < 4:
				matches.append(pm)
		return matches

	def _choose_best_file(self, files):
		files = sorted(
			files,
			key=lambda f: SanitizedRelFile(base=settings.get("output.base_dir"), file_path=f.path).size(),
			reverse=True
		)
		return files[0], files[1:]

	def _upgrade_file(self, new_file, old_file):
		print('Upgrading old file:', old_file.id, old_file.path, ' -> ', new_file.id, new_file.path)
		self._session.query(URL). \
			filter(URL.file_id == old_file.id). \
			update({URL.file_id: new_file.id})
		file = SanitizedRelFile(base=settings.get("output.base_dir"), file_path=old_file.path)
		if file.is_file():
			file.delete_file()

	def _prune(self):
		orphans = self._session.query(File).filter(~File.urls.any()).delete(synchronize_session='fetch')
		self._session.commit()
		if orphans:
			print("Deleted orphan Files:", orphans)


class FileHasher:
	@staticmethod
	def get_best_hash(filename):
		"""
		Attempts to hash the given file with the best possible hash (either a direct SHA1 or a Visual)
		:param filename: The path to hash.
		"""
		try:
			image = Image.open(filename)
			if FileHasher._is_animated(image):
				# Could dhash gifs to compare them, but that's a lot of memory for little likely gain.
				best_hash = FileHasher._sha_hash(filename)
			else:
				best_hash = FileHasher._dhash(image)
			image.close()
		except IOError:
			# Pillow can't load the file, so we have to assume it's not an image.
			best_hash = FileHasher._sha_hash(filename)
		return best_hash

	@staticmethod
	def _is_animated(image):
		"""
		Checks if the given Image object is an animated GIF
		"""
		try:
			image.seek(1)
		except EOFError:
			return False
		else:
			return True

	@staticmethod
	def _dhash(image, hash_size=8):
		"""
		Generates a Visual Difference Hash of the given Image Object.
		Credit to: https://github.com/JohannesBuchner/imagehash
		"""
		# Grayscale and shrink the image in one step.
		image = image.convert('L').resize(
			(hash_size + 1, hash_size),
			Image.ANTIALIAS,
		)
		# Compare adjacent pixels.
		difference = []
		for row in range(hash_size):
			for col in range(hash_size):
				pixel_left = image.getpixel((col, row))
				pixel_right = image.getpixel((col + 1, row))
				difference.append(pixel_left > pixel_right)
		# Convert the binary array to a hexadecimal string.
		decimal_value = 0
		hex_string = []
		for index, value in enumerate(difference):
			if value:
				decimal_value += 2**(index % 8)
			if (index % 8) == 7:
				hex_string.append(hex(decimal_value)[2:].rjust(2, '0'))
				decimal_value = 0
		return ''.join(hex_string)

	@staticmethod
	def _sha_hash(filename):
		try:
			with open(filename, 'rb', buffering=0) as f:
				h = hashlib.sha1()
				for b in iter(lambda: f.read(1024*1024), b''):
					h.update(b)
				return h.hexdigest()
		except IOError:
			return None

	@staticmethod
	def hamming_distance(s1, s2):
		"""Return the Hamming distance between equal-length sequences"""
		if len(s1) != len(s2):
			return 9999
		return sum(el1 != el2 for el1, el2 in zip(s1, s2))

