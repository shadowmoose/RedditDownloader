import static.settings as settings
from processing.rel_file import RelFile, SanitizedRelFile
from static import stringutil
from sql import File


def choose_file_name(url, session):
	base = _choose_base_name(url).relative()
	idx = 1
	nb = base + " - %s"
	while session.query(File.path).filter(File.path.like(base+"%")).first():
		idx += 1
		base = nb % idx
	return base


def _choose_base_name(url):
	"""
	Generate the base file name, missing any extensions.
	Auto-converts "Album" URLs into directories, with the leading file index added.
	:param url: An sql.URL object.
	:return: The RelFile generated, with the path variables inserted and formatted.
	"""
	post = url.post
	dir_pattern = './%s' % settings.save_subdir()
	file_pattern = '%s/%s' % (dir_pattern, settings.save_filename())
	if url.album_id is not None:
		file_pattern += '/%s - ' % url.album_order  # if this URL is an album file, the filename path turns into a dir.
	output = RelFile(base=settings.get("output.base_dir"), file_path=file_pattern)

	basefile = stringutil.insert_vars(output.absolute(), post)

	if basefile is None:
		raise Exception("Unable to name file properly!")  # TODO: Better handling.

	return SanitizedRelFile(base=settings.get("output.base_dir"), full_file_path=basefile)
