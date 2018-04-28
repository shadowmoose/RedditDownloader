"""
	The Hash jar handles hashing - and then storing - all the possible files downloaded.
	It is used by the Element Processor to deduplicated downloaded files.

	Though not a flawless solution (files are still downloaded locally first), it's better than nothing.

	Fueled by code from https://github.com/JohannesBuchner/imagehash,
	so please head there and read their licence/thank them!
"""
import hashlib
import os.path
from PIL import Image
from util import stringutil
from util import manifest


def add_hash(filename):
	"""
	Add the given file to the Hash jar.
	:param filename: The path to the file to add.
	:return: ([Is New File], existing_file_path)
	"""
	if not filename or not os.path.exists(filename) or os.path.isdir(filename):
		# Skip directories.
		return True, None

	pre = manifest.get_file_hash(filename)
	lmt = os.path.getmtime(filename)
	if pre:
		if lmt == pre['lastmtime']:
			# Hash already exists and file hasn't changed since.
			#print('Hashjar: File unchanged: %s' % filename)
			return False, filename

	#print('Hashjar: Hashing file: %s' % filename)
	#manifest.set_metadata('hashed_files', int(manifest.get_metadata('hashed_files', '0')) + 1)
	#manifest.set_metadata(filename, '%s | %s' % (pre['lastmtime'] if pre else None, lmt))

	_, final_hash = _get_best_hash(filename)
	if not final_hash: #!cover
		stringutil.error("HashCheck :: Error hit hashing file, passing file as new.")
		return True, None

	#print("\tHashCheck :: Fingerprinting new image...", end='\r')
	_it = manifest.hash_iterator(len(final_hash) )
	for h in _it:
		dist = _hamming_distance(h['hash'], final_hash)
		if dist < 4:
			#print('\tHashCheck :: Distance matches existing file (%s,%s): %s' % (final_hash, h, dist))
			_it.send(True) # Release DB generator.
			return False, h['file_path']
	#print('\tHashCheck :: File is unique. Saved successfully.')

	manifest.put_file_hash(filename, final_hash, lmt)
	return True, None


def _get_best_hash(filename):
	"""
	Attempts to hash the given file with the best possible hash (either a direct SHA1 or a Visual)
	:param filename: The path to hash.
	:return:
	"""
	try:
		image = Image.open(filename)
		if _is_animated(image): #!cover
			#best_hash = _hash_gif(image)
			# Could dhash gifs to compare them, but that's a lot of memory for little likely gain.
			best_hash = _sha_hash(filename)
			is_image = False
		else:
			best_hash = _dhash(image)
			is_image = True
	except IOError:
		# Pillow can't load the file, so we have to assume it's not an image.
		best_hash = _sha_hash(filename)
		is_image = False
	return is_image, best_hash


def _is_animated(image): #!cover
	"""
	Checks if the given Image object is an animated GIF
	"""
	try:
		image.seek(1)
	except EOFError:
		return False
	else:
		return True


def _hash_gif(image): #!cover
	"""
	Build a hash for animated gif objects.
	"""
	print("Building gif hash.")
	gif_hashes = None
	try:
		mypalette = image.getpalette()
		gif_hashes = []
		while 1:
			image.putpalette(mypalette)
			sub = Image.new("RGBA", image.size)
			sub.paste(image)
			gif_hashes.append(_dhash(sub))
			image.seek(image.tell() + 1)
	except EOFError:
		pass # end of sequence
	if gif_hashes:
		return 'gif:'+('+'.join(gif_hashes))
	return None


def _dhash(image, hash_size = 8):
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


def _sha_hash(filename):
	try:
		with open(filename, 'rb', buffering=0) as f:
			h = hashlib.sha1()
			for b in iter(lambda : f.read(128*1024), b''):
				h.update(b)
			return h.hexdigest()
	except IOError:
		return None


def _hamming_distance(s1, s2):
	"""Return the Hamming distance between equal-length sequences"""
	if len(s1) != len(s2):
		raise 9999
	return sum(el1 != el2 for el1, el2 in zip(s1, s2))
