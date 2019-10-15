from sqlalchemy import Column, String, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship

import sql


class URL(sql.Base):
	__tablename__ = 'urls'
	id = Column(Integer, primary_key=True)
	address = Column(String, nullable=False, index=True)
	processed = Column(Boolean, nullable=False, default=False, index=True)
	failed = Column(Boolean, nullable=False, default=False, index=True)
	failure_reason = Column(String, default=None)
	post_id = Column(String, ForeignKey('posts.reddit_id'), index=True)
	post = relationship("Post", back_populates="urls")
	album_id = Column(String, default=None, index=True)
	album_order = Column(Integer, default=0)
	album_is_parent = Column(Boolean, default=False, nullable=False)
	last_handler = Column(String, default=None)
	file_id = Column(String, ForeignKey('files.id'), index=True)
	file = relationship("File", back_populates="urls")

	def __repr__(self):
		failure = ""
		if self.failed:
			failure = ', Failed, Reason: "%s"' % self.failure_reason
		return "<URL ID: %s, Address: %s, Downloaded: %s %s>" % (self.id, self.address, self.processed, failure)

	@staticmethod
	def make_url(address, post, album_key, album_order):
		"""
		Convenience function to generate and return a URL object.
		"""
		return URL(
			address=address,
			post_id=post.reddit_id,
			album_id=album_key,
			album_order=album_order
		)
