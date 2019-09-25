from sqlalchemy import Column, String, Integer, Boolean
from sqlalchemy.orm import relationship

import sql


class File(sql.Base):
	__tablename__ = 'files'
	id = Column(Integer, primary_key=True)
	path = Column(String, nullable=False, unique=True)
	hash = Column(String, default=None, index=True)
	downloaded = Column(Boolean, nullable=False, default=False)
	urls = relationship("URL", back_populates="file")

	def __repr__(self):
		return '<File ID: %s, Path: "%s", Hash: "%s">' % (self.id, self.path, self.hash)
