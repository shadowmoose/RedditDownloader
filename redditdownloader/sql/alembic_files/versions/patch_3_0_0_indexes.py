""" Fix missing all missing index.

Revision ID: f8035abd1974
Revises: Accidentally set up an index for a few fields without versioning, and they need to be corrected here. Oops.
Create Date: 2019-11-13 23:50:48.755182

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = 'patch_3_0_0'
down_revision = 'f8035abd1974'
branch_labels = None
depends_on = None

missing_index = {
	'files': {
		'ix_files_hash': 'hash',
	},
	'urls': {
		'ix_urls_address': 'address',
		'ix_urls_album_id': 'album_id',
		'ix_urls_failed': 'failed',
		'ix_urls_file_id': 'file_id',
		'ix_urls_post_id': 'post_id',
		'ix_urls_processed': 'processed'
	}
}


def upgrade():
	for table_name, v in missing_index.items():
		for iname, field in v.items():
			try:
				op.create_index(iname, table_name, [field], unique=False)
			except Exception:
				pass


def downgrade():
	for table_name, v in missing_index.items():
		for iname, field in v.items():
			try:
				op.drop_index(iname, table_name)
			except Exception:
				pass
