"""
	This is a tool to build Alembic SQLite Migration files.
	It should not be useful for any end-user, and only exists to simplify generating database changes between releases.

	To Use:
		Assure that your database is at the "head" migration: `alembic -x dbPath=../path-to/sqlite.sqlite upgrade head`
		Run this util, and enter a Migration name.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
import sql
from alembic import command
from static import console
from static import settings
import static.filesystem as fs


def make_migration():
	conn = sql.session()
	alembic_cfg, script_, context = sql.get_alembic_ctx(conn)
	message = console.string('Enter a message for the migration')
	res = command.revision(message=message, autogenerate=True, config=alembic_cfg)
	print('Generated Migration:', res)
	print('Finished.')


if __name__ == '__main__':
	settings.load(fs.find_file('settings.json'))
	sql.init_from_settings()
	make_migration()
