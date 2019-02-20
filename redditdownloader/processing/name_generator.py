import static.settings as settings
from processing.wrappers.rel_file import RelFile, SanitizedRelFile
from static import stringutil
from sql import File, URL


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
	Generate the base file name, missing any extensions.
	Auto-converts "Album" URLs into directories, with the leading file index added.
	:param post: An sql.Post object.
	:return: The RelFile generated, with the path variables inserted and formatted.
	"""
	dir_pattern = './%s' % settings.save_subdir()
	file_pattern = '%s/%s' % (dir_pattern, settings.save_filename())

	output = RelFile(base=settings.get("output.base_dir"), file_path=file_pattern)

	basefile = stringutil.insert_vars(output.absolute(), post).strip().rstrip('. ')

	if not basefile:
		raise Exception("Unable to name file properly!")  # TODO: Better handling.

	return SanitizedRelFile(base=settings.get("output.base_dir"), full_file_path=basefile)


def _add_album(url, file_pattern, album_size):
	if url.album_id is not None:
		order = str(url.album_order).rjust(len(str(album_size)), '0')
		file_pattern += '/%s' % order  # if this URL is an album file, the filename path turns into a dir.
	return file_pattern
