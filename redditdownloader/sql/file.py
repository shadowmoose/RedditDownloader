from sqlalchemy import Column, String, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship

import sql


class File(sql.Base):
	__tablename__ = 'files'
	id = Column(Integer, primary_key=True)
	path = Column(String, nullable=False, unique=True)
	hash = Column(String, default=None)
	downloaded = Column(Boolean, nullable=False, default=False)
	url_id = Column(String, ForeignKey('urls.id'))
	url = relationship("URL", back_populates="files")

	def __repr__(self):
		return '<File ID: %s, Path: "%s", Hash: "%s">' % (self.id, self.path, self.hash)
