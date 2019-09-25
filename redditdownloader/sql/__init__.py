"""
The SqlAlchemy static wrapper class.
The Sessions created are Thread-safe, but Thread-local in scope.
Its objects should not be shared across Processes or Threads.
"""

import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import or_
from processing.wrappers import SanitizedRelFile
from static import settings
import os

Base = declarative_base()

_engine = None
_Session = None


def init(db_path=":memory:"):
	"""
	Initialize the DB, a required function to access the database.
	Creates the DB file if it does not already exist.
	:param db_path:
	:return:
	"""
	global _engine, _Session
	if _Session and _engine:
		return
	create_new = False
	if db_path != ':memory:':
		db_path = os.path.abspath(db_path)
		create_new = not os.path.exists(db_path)
	_engine = sqlalchemy.create_engine('sqlite:///%s' % db_path)  # , echo=True)
	session_factory = sessionmaker(bind=_engine)
	_Session = scoped_session(session_factory)
	if create_new:
		_create()


def init_from_settings():
	""" Builds the database file using the Settings currently loaded. """
	db_file = SanitizedRelFile(base=settings.get("output.base_dir"), file_path="manifest.sqlite")
	db_file.mkdirs()
	init(db_file.absolute())


def _create():
	Base.metadata.create_all(_engine)
	print("\tCreated Database file.")
	session().execute("PRAGMA journal_mode=WAL")
	print("\t+Activated WAL Mode.")


def session():
	"""
	Create a Thread-local Session object, the entrypoint to the Database.
	:return:
	"""
	if not _Session or not _engine:
		init_from_settings()
	# noinspection PyCallingNonCallable
	return _Session()


def close():
	_Session.close()


# Import ORM classes at bottom so they can access this package safely.
from sql.file import File
from sql.post import Post
from sql.url import URL


class Searcher:
	def __init__(self, Clazz):
		self.clazz = Clazz

	def _is_searchable(self, field, f_type):
		if field.startswith('_') or field.endswith('id'):
			return False
		return str(f_type).lower() == 'varchar'

	def get_searchable_fields(self):
		return [c.name for c in self.clazz.__table__.columns if self._is_searchable(c.name, c.type)]

	def search_field_conditions(self, search_fields, term):
		term = str(term).strip("%")
		ok_fields = self.get_searchable_fields()
		conds = [getattr(self.clazz, field).like("%" + term + "%") for field in search_fields if field in ok_fields]
		return conds


class PostSearcher(Searcher):
	def __init__(self, current_session):
		super().__init__(Post)
		self.session = current_session

	def search_fields(self, fields, term):
		""" Search for Posts with any of the given fields matching the given term. """
		conds = self.search_field_conditions(fields, term)
		return self.session\
			.query(Post)\
			.join(URL)\
			.join(File)\
			.filter(or_(*conds)) \
			.filter((URL.processed != False))\
			.filter(URL.failed != True).all()
