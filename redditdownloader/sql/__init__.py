"""
The SqlAlchemy static wrapper class.
The Sessions created are Thread-safe, but Thread-local in scope.
Its objects should not be shared across Processes or Threads.
"""

import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
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


def _create():
	Base.metadata.create_all(_engine)
	print("\tCreated Database file.")


def session():
	"""
	Create a Thread-local Session object, the entrypoint to the Database.
	:return:
	"""
	if not _Session:
		raise Exception("The Database has not been initialized! Unable to create Session.")
	# noinspection PyCallingNonCallable
	return _Session()


# Import ORM classes at bottom so they can access this package safely.
from sql.file import File
from sql.post import Post
from sql.url import URL
