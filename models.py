from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, Table
from sqlalchemy.orm import relationship
from database import Base

user_video_favorites = Table(
    "user_video_favorites",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("video_id", Integer, ForeignKey("videos.id"), primary_key=True)
)

user_comment_favorites = Table(
    "user_comment_favorites",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("comment_id", Integer, ForeignKey("comments.id"), primary_key=True)
)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)

    videos = relationship("Video", back_populates="owner", cascade="all, delete")
    comments = relationship("Comment", back_populates="owner", cascade="all, delete")
    favorite_videos = relationship(
        "Video",
        secondary=user_video_favorites,
        back_populates="liked_by_users"
    )
    favorite_comments = relationship(
        "Comment",
        secondary=user_comment_favorites,
        back_populates="liked_by_users"
    )


class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    likes = Column(Integer, default=0, server_default="0", nullable=False)
    dislikes = Column(Integer, default=0, server_default="0", nullable=False)

    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="videos")

    comments = relationship("Comment", back_populates="video", cascade="all, delete")

    liked_by_users = relationship(
        "User",
        secondary=user_video_favorites,
        back_populates="favorite_videos"
    )


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String, nullable=False)
    likes = Column(Integer, default=0, server_default="0", nullable=False)
    dislikes = Column(Integer, default=0, server_default="0", nullable=False)
    creator_like = Column(Boolean, index=True)
    date = Column(DateTime, index=True)

    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="comments")

    video_id = Column(Integer, ForeignKey("videos.id"))
    video = relationship("Video", back_populates="comments")

    liked_by_users = relationship(
        "User",
        secondary=user_comment_favorites,
        back_populates="favorite_comments"
    )