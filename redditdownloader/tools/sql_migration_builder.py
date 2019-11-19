"""
	This is a development tool to build Alembic SQLite Migration files.
	It should not be useful for any end-user, and only exists to simplify generating database changes between releases.

	Any migration deltas generated will be based off the current DB Model state at the time of execution.
	The suggested method of updating to the "head" migration is to simply run RMD, and confirm the migration works.

	To Use:
		1. Assure that your database is at the "head" migration. RMD should do this autmatically, or run:
		 	`alembic -x dbPath=../path-to/sqlite.sqlite upgrade head`
		2. Run this util, and enter a Migration name.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
import sql
from alembic import command
from static import console
from static import settings
import static.filesystem as fs
import shutil
from datetime import datetime


def make_migration():
	conn = sql.session()
	alembic_cfg, script_, context = sql.get_alembic_ctx(conn)
	message = console.string('Enter a message for the migration')
	if not message:
		print('Skipping migration.')
		return
	res = command.revision(message=message, autogenerate=True, config=alembic_cfg)
	print('Generated Migration:', res)
	print('Finished.')


if __name__ == '__main__':
	settings.load(fs.find_file('settings.json'))
	sql.init_from_settings()
	# noinspection PyProtectedMember
	pth = sql._db_path
	bkup = ('%s-bkup-%s.sqlite' % (pth, str(datetime.now()).replace(':', '.')))
	shutil.copy2(pth, bkup)
	make_migration()
