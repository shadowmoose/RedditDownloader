import static.settings as settings
from processing.wrappers.rel_file import RelFile, SanitizedRelFile
import pathvalidate
from sql import File, URL


_pattern_array = None


def choose_file_name(url, post, session, album_size=1):
	base = _choose_base_name(post).relative()
	idx = 1
	nb = base + " - %s"
	while _get_matching(base=base, url=url, session=session):
		idx += 1
		base = nb % idx
	base = _add_album(url, base, album_size=album_size)
	return base


def _get_matching(base, url, session):
	if url.album_id:
		aid = url.album_id
		# Get matching bases, where they aren't from the same album.
		return session.query(File).join(URL).filter(File.path.like(base+"%")).filter(URL.album_id != aid).first()
	else:
		# Get any matching base, because this isn't an album file.
		return session.query(File).filter(File.path.like(base+"%")).first()


def _choose_base_name(post):
	"""
	Generate the base file name, missing any extensions. Respects a maximum absolute filepath length.
	:param post: An sql.Post object.
	:return: The RelFile generated, with the path variables inserted and formatted.
	"""
	global _pattern_array
	if not _pattern_array:
		file_pattern = './%s' % settings.get('output.file_name_pattern').strip('/\\ .')
		_pattern_array = _parse_pattern(file_pattern, post.__dict__)
	max_len = 200
	length = min(max_len, max(len(str(post.__dict__[k])) for k in post.__dict__.keys()))
	while max_len:
		output = SanitizedRelFile(base=settings.get("output.base_dir"), file_path=_build_str(post.__dict__, length))
		if len(output.absolute()) <= max_len:
			return output
		length -= 1
	raise Exception("Unable to name file properly! Filename is likely too long!")


def _add_album(url, file_pattern, album_size):
	if url.album_id is not None:
		order = str(url.album_order).rjust(len(str(album_size)), '0')
		file_pattern += '/%s' % order  # if this URL is an album file, the filename path turns into a dir.
	return file_pattern


def _parse_pattern(string_in, inserts):
	# Buids a pattern array, which can be used to build a dynamic-variable string.
	st = {'txt': '', 'var': False}
	ret = []
	open_brackets = 0
	for c in string_in:
		if c == '[' or c == ']':
			if open_brackets and st['txt'].strip() and st['txt'].strip() in inserts and not st['txt'].startswith('_'):
				st['txt'] = st['txt'].strip()
				st['var'] = True
			ret.append(st)
			st = {'txt': '', 'var': False}
			open_brackets += 1 if c == '[' else -1
		else:
			st['txt'] += c

	if open_brackets != 0:
		reason = '[' if open_brackets > 0 else ']'
		raise Exception("File output pattern has too many '%s' brackets: %s" % (reason, open_brackets))
	ret.append(st)
	return list(filter(lambda x: x, ret))


def _build_str(inserts, max_length=100):
	""" Builds a string, inserting variables from the given Object. Assumes the pattern_array has been generated. """
	if not _pattern_array:
		raise Exception("Filename pattern array was not built!")
	ret = ''
	for a in _pattern_array:
		if a['var']:
			ins = ''.join(_filename(str(inserts[a['txt']]))[0:max_length]).strip()
			ret += ins
		else:
			ret += a['txt']
	return ret


def _filename(f_name):
	""" Format the given string into an acceptable filename. """
	ret = f_name
	# noinspection PyBroadException
	try:
		ret = pathvalidate.sanitize_filename(ret, '_').strip(' ./\\')
	except Exception:
		ret = '_'
	if len(ret) == 0:
		return '_'
	return ret

