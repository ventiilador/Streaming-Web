from sqlalchemy import Column, Float, Integer, String, ForeignKey, Boolean, DateTime, Table
from datetime import datetime
from sqlalchemy.orm import relationship
from database import Base

user_video_favorites = Table(
    "user_video_favorites",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("video_id", Integer, ForeignKey("videos.id"), primary_key=True)
)

user_video_hated = Table(
    "user_video_hated",
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

user_comment_hated = Table(
    "user_comment_hated",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("comment_id", Integer, ForeignKey("comments.id"), primary_key=True)
)

user_subscriptions = Table(
    "user_subscriptions",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("channel_id", Integer, ForeignKey("users.id"), primary_key=True)
)

video_hashtags = Table(
    "video_hashtags",
    Base.metadata,
    Column("video_id", Integer, ForeignKey("videos.id"), primary_key=True),
    Column("hashtag_id", Integer, ForeignKey("hashtags.id"), primary_key=True)
)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    subscribers_count = Column(Integer, default=0, server_default="0", nullable=False)
    biography = Column(String)
    profile_extension = Column(String)
    private_account = Column(Boolean, default=False, nullable=False)
    last_time_active = Column(DateTime)
    online = Column(Boolean, default=False)

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

    subscriptions = relationship(
        "User",
        secondary=user_subscriptions,
        primaryjoin=id==user_subscriptions.c.user_id,
        secondaryjoin=id==user_subscriptions.c.channel_id,
        back_populates="subscribers"
    )

    subscribers = relationship(
        "User",
        secondary=user_subscriptions,
        primaryjoin=id==user_subscriptions.c.channel_id,
        secondaryjoin=id==user_subscriptions.c.user_id,
        back_populates="subscriptions"
    )

    preferences = relationship("UserPreference", back_populates="user", cascade="all, delete")

    followed = relationship("FollowUp", foreign_keys="FollowUp.follower_id", back_populates="follower")
    
    followers = relationship("FollowUp", foreign_keys="FollowUp.followed_id", back_populates="followed")

    sent_messages = relationship(
        "PrivateMessage",
        foreign_keys="PrivateMessage.sender_id",
        back_populates="sender",
        cascade="all, delete-orphan"
    )

    received_messages = relationship(
        "PrivateMessage",
        foreign_keys="PrivateMessage.recipient_id",
        back_populates="recipient",
        cascade="all, delete-orphan"
    )


class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    video_extension = Column(String, nullable=False)
    miniature_extension = Column(String, nullable=False)
    upload_date = Column(DateTime)
    views = Column(Integer, default=0, server_default="0", nullable=False)
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

    hashtags = relationship(
        "Hashtag",
        secondary=video_hashtags,
        back_populates="videos"
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


class Hashtag(Base):
    __tablename__ = "hashtags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

    videos = relationship(
        "Video",
        secondary=video_hashtags,
        back_populates="hashtags"
    )

class UserPreference(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    hashtag_id = Column(Integer, ForeignKey("hashtags.id"))

    weight = Column(Float, default=1.0) 

    user = relationship("User", back_populates="preferences")
    hashtag = relationship("Hashtag")


class FollowUp(Base):
    __tablename__ = "follow_up"

    id = Column(Integer, primary_key=True)
    
    follower_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    followed_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(DateTime)

    follower = relationship("User", foreign_keys=[follower_id], back_populates="followed")
    followed = relationship("User", foreign_keys=[followed_id], back_populates="followers")


class PrivateMessage(Base):
    __tablename__ = "private_messages"

    id = Column(Integer, primary_key=True)
    content = Column(String, nullable=False)
    date = Column(DateTime, nullable=False)

    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    recipient_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    sender = relationship("User", foreign_keys=[sender_id], back_populates="sent_messages")
    recipient = relationship("User", foreign_keys=[recipient_id], back_populates="received_messages")