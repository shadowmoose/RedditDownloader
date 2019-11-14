from sqlalchemy import Column, String, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship

import sql


class File(sql.Base):
	__tablename__ = 'files'
	id = Column(Integer, primary_key=True)
	path = Column(String, nullable=False, unique=True)
	hash = relationship("Hash", uselist=False, back_populates="file")
	downloaded = Column(Boolean, nullable=False, default=False)
	urls = relationship("URL", back_populates="file")

	def __repr__(self):
		return '<File ID: %s, Path: "%s", Hash: "%s">' % (self.id, self.path, self.hash)


class Hash(sql.Base):
	__tablename__ = 'hashes'
	id = Column(Integer, primary_key=True)
	file_id = Column(String, ForeignKey('files.id'), index=True)
	file = relationship("File", back_populates="hash")
	full_hash = Column(String, index=True)
	p1 = Column(String, index=True)
	p2 = Column(String, index=True)
	p3 = Column(String, index=True)
	p4 = Column(String, index=True)

	def __repr__(self):
		return '<Hash ID: %s, Full Hash: "%s">' % (self.id, self.full_hash)

	@staticmethod
	def split_hash(hash_string):
		""" Split the given Hash string into sections, formatted to fit in the Hash table. """
		return [hash_string[i:i + 4] for i in range(0, len(hash_string), 4)]

	@staticmethod
	def make_hash(file, hash_string):
		"""
		Convenience function to generate and return a Hash object.
		"""
		if len(hash_string) != 16:
			return Hash(
				file_id=file.id,
				full_hash=hash_string
			)
		else:
			sp = Hash.split_hash(hash_string)
			return Hash(
				file_id=file.id,
				full_hash=hash_string,
				p1=sp[0],
				p2=sp[1],
				p3=sp[2],
				p4=sp[3],
			)
