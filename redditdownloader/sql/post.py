from sqlalchemy import Column, String, Integer, Boolean
from sqlalchemy.orm import relationship
import sql


class Post(sql.Base):
	__tablename__ = 'posts'
	reddit_id = Column(String, primary_key=True)
	author = Column(String)
	urls = relationship("URL", back_populates="post")
	type = Column(String, nullable=False)
	title = Column(String, nullable=False)
	body = Column(String)
	parent_id = Column(String, default=None)
	subreddit = Column(String, default=None)

	over_18 = Column(Boolean, nullable=False, default=False)
	created_utc = Column(Integer, nullable=False)
	num_comments = Column(Integer, nullable=False)
	score = Column(Integer, nullable=False)
	source_alias = Column(String)

	def __repr__(self):
		return '<Post ID: %s, Author: "%s", URLs: "%s">' % (self.reddit_id, self.author, len(self.urls))

	@staticmethod
	def convert_element_to_post(re):
		""" Converts the given RedditElement into a Post object. """
		return Post(
			reddit_id=re.id,
			author=re.author,
			type=re.type,
			title=re.title,
			body=re.body,
			parent_id=re.parent,
			subreddit=re.subreddit,
			over_18=re.over_18,
			created_utc=re.created_utc,
			num_comments=re.num_comments,
			score=re.score,
			source_alias=re.source_alias
		)
