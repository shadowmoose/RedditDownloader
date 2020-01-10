"""
The SqlAlchemy static wrapper class.
The Sessions created are Thread-safe, but Thread-local in scope.
Its objects should not be shared across Processes or Threads.
"""

import json
import traceback

import sqlalchemy
from alembic import command
from alembic import script
from alembic.config import Config
from alembic.runtime import migration
from sqlalchemy import or_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
import os
import shutil
import sys
from processing.wrappers import SanitizedRelFile
from static import settings

Base = declarative_base()

_sqlite_uri = None
_db_path = None
_engine = None
_Session = None


def init(db_path=":memory:"):
	"""
	Initialize the DB, a required function to access the database.
	Creates the DB file if it does not already exist.
	:param db_path:
	:return:
	"""
	global _engine, _Session, _sqlite_uri, _db_path
	if _Session and _engine:
		return
	_sqlite_uri = 'sqlite:///%s' % db_path
	create_new = False
	if db_path != ':memory:':
		db_path = os.path.abspath(db_path)
		create_new = not os.path.exists(db_path)
	_db_path = db_path
	_engine = sqlalchemy.create_engine(_sqlite_uri)  # , echo=True)
	session_factory = sessionmaker(bind=_engine)
	_Session = scoped_session(session_factory)
	if create_new:
		_create()
	_run_migrations(session())


def init_from_settings():
	""" Builds the database file using the Settings currently loaded. """
	db_file = SanitizedRelFile(base=settings.get("output.base_dir"), file_path="manifest.sqlite")
	db_file.mkdirs()
	init(db_file.absolute())


def _create():
	sess = session()
	sess.execute("PRAGMA journal_mode=WAL")
	sess.commit()
	print("\t+Activated WAL Mode.")
	sess.commit()


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


class make_backup(object):
	""" Context handler, creates backup file that is deleted on close, or reverted on Exception. """
	def __init__(self, original_path):
		self.original_path = original_path

	def __enter__(self):
		self.bkup_path = self.original_path + '-bkup.sqlite'
		shutil.copy2(self.original_path, self.bkup_path)
		return self.bkup_path

	def __exit__(self, exc_type, exc_val, exc_tb):
		try:
			if any([exc_type, exc_tb, exc_val]):
				print(exc_val)
				shutil.copy(self.bkup_path, self.original_path)
				print('Rolled back file:', self.original_path, '  From:', self.bkup_path)
				os.remove(self.bkup_path)
				sys.exit(45)
			os.remove(self.bkup_path)
		except Exception as err:
			print(err)


def get_alembic_ctx(conn):
	""" Gets a full suite of Alembic objects, pre-initialized with all relevant details. """
	conf = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../alembic.ini'))
	alem_conf_loc = os.path.abspath(os.path.join(os.path.dirname(__file__), './alembic_files/'))
	alembic_cfg = Config(conf)
	connection = conn.connection()
	alembic_cfg.attributes['connection'] = connection
	alembic_cfg.set_main_option('script_location', alem_conf_loc)
	scr = script.ScriptDirectory.from_config(alembic_cfg)
	context = migration.MigrationContext.configure(alembic_cfg.attributes['connection'])
	return alembic_cfg, scr, context


def _run_migrations(conn) -> None:
	try:
		_check_legacy(conn)
		alembic_cfg, script_, context = get_alembic_ctx(conn)
		if context.get_current_revision() != script_.get_current_head():
			print('Database is not up to date! %s < %s' % (context.get_current_revision(), script_.get_current_head()))
			with make_backup(_db_path):
				# noinspection PyBroadException
				try:
					command.upgrade(alembic_cfg, 'head')
					print('\t+Upgraded manifest to version', context.get_current_revision())
					conn.commit()
				except Exception:
					traceback.print_exc()
					conn.rollback()
					raise Exception('Failed to upgrade database!')
	finally:
		conn.close()


def _check_legacy(sess):
	""" Check if there is a valid table structure, but it is unversioned. If so, apply default base 3.0.0 version. """
	rs = sess.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="posts";')
	if rs.fetchone():
		alembic_cfg, script_, context = get_alembic_ctx(sess)
		if not context.get_current_revision():
			print("Versioning pre-alembic < 3.0.0 DB.")
			# Stamp to 3.0.0 structure, which predated Alembic:
			command.stamp(config=alembic_cfg, revision='f8035abd1974', purge=True)
			sess.commit()


# Import ORM classes at bottom so they can access this package safely.
from sql.file import File, Hash
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
			.filter(URL.failed != True)\
			.all()


def _iterable(obj):
	""" Check if the given Object is an iterable, non-string collection. """
	if str(obj) == obj:
		return False
	try:
		iter(obj)
		return True
	except TypeError:
		return False


def _encode_obj(obj):
	""" Recursively collapse the given Object into one that can be JSON-encoded."""
	ret = {}
	for k, v in obj.__dict__.items():
		if k.startswith('_'):
			continue
		if hasattr(v, '_sa_instance_state'):
			ret[k] = _encode_obj(v)
		elif _iterable(v):
			ret[k] = [_encode_obj(i) for i in v]
		else:
			ret[k] = v
	return ret


def encode_safe(obj, stringify=False, indent=None):
	"""
		Encode the given object(s), into new Objects that are safe for serialization.
		Supports automatic JSON encoding, single DB objects, or lists of DB Objects.
	"""
	if _iterable(obj):
		obj = [_encode_obj(o) for o in obj]
	else:
		obj = _encode_obj(obj)
	if stringify:
		obj = json.dumps(obj, indent=indent)
	return obj
