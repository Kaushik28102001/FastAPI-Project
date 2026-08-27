from __future__ import annotations

from datetime import UTC, datetime, date

from sqlalchemy import (
    DateTime,
    Date,
    ForeignKey,
    Integer,
    String,
    Text,
    Boolean,
    Column,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from database import Base


# =========================================================
# USER
# =========================================================

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(120),
        unique=True,
        nullable=False,
    )

    password_hash: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    image_file: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
        default=None,
    )

    is_admin: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        server_default="0",
    )

    # User -> Posts
    posts: Mapped[list["Post"]] = relationship(     
    "Post",
    back_populates="author",
    cascade="all, delete-orphan",
    )

    # User -> Password Reset Tokens
    reset_tokens: Mapped[list["PasswordResetToken"]] = relationship(
        "PasswordResetToken",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    post_likes: Mapped[list["PostLike"]] = relationship(
    "PostLike",
    back_populates="user",
    cascade="all, delete-orphan",
    )

    comments: Mapped[list["PostComment"]] = relationship(
        "PostComment",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    reposts: Mapped[list["Repost"]] = relationship(
        "Repost",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    @property
    def image_path(self) -> str:
        if self.image_file:
            return f"/media/profile_pics/{self.image_file}"

        return "/static/profile_pics/default.jpg"


# =========================================================
# POST
# =========================================================

class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    short_content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    image_file: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
        default=None,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    date_posted: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )

    # Post -> User
    author: Mapped["User"] = relationship(
        "User",
        back_populates="posts",
    )

    post_likes: Mapped[list["PostLike"]] = relationship(
        "PostLike",
        back_populates="post",
        cascade="all, delete-orphan",
    )

    comments: Mapped[list["PostComment"]] = relationship(
        "PostComment",
        back_populates="post",
        cascade="all, delete-orphan",
    )

    reposts: Mapped[list["Repost"]] = relationship(
        "Repost",
        back_populates="post",
        cascade="all, delete-orphan",
    )

    @property
    def image_path(self) -> str:
        if self.image_file:
            return f"/media/post_pics/{self.image_file}"

        return "/static/post_pics/default.jpg"


# =========================================================
# PASSWORD RESET TOKEN
# =========================================================

class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    token_hash: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False,
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="reset_tokens",
    )


# =========================================================
# ANNOUNCEMENT
# =========================================================

class Announcement(Base):
    __tablename__ = "announcements"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )

    comments: Mapped[list["AnnouncementComment"]] = relationship(
        "AnnouncementComment",
        cascade="all, delete-orphan",
    )


# =========================================================
# CALENDAR EVENT
# =========================================================

class CalendarEvent(Base):
    __tablename__ = "calendar_events"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    event_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )


# =========================================================
# ANNOUNCEMENT COMMENT
# =========================================================

class AnnouncementComment(Base):
    __tablename__ = "announcement_comments"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    announcement_id: Mapped[int] = mapped_column(
        ForeignKey("announcements.id"),
        nullable=False,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    comment: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )


# =========================================================
# POST COMMENT
# =========================================================

class PostComment(Base):
    __tablename__ = "post_comments"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    post_id: Mapped[int] = mapped_column(
        ForeignKey("posts.id"),
        nullable=False,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    comment: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )

    # Comment -> Post
    post: Mapped["Post"] = relationship(
        "Post",
        back_populates="comments",
    )

    # Comment -> User
    user: Mapped["User"] = relationship(
        "User",
        back_populates="comments",
    )


# =========================================================
# POST LIKE
# =========================================================

class PostLike(Base):
    __tablename__ = "post_likes"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    post_id: Mapped[int] = mapped_column(
        ForeignKey("posts.id"),
        nullable=False,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    # Like -> Post
    post: Mapped["Post"] = relationship(
        "Post",
        back_populates="post_likes",
    )

    # Like -> User
    user: Mapped["User"] = relationship(
        "User",
        back_populates="post_likes",
    )


# =========================================================
# ANNOUNCEMENT LIKE
# =========================================================

class AnnouncementLike(Base):
    __tablename__ = "announcement_likes"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    announcement_id: Mapped[int] = mapped_column(
        ForeignKey("announcements.id"),
        nullable=False,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )


# =========================================================
# REPOST
# =========================================================

class Repost(Base):
    __tablename__ = "reposts"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    post_id: Mapped[int] = mapped_column(
        ForeignKey("posts.id"),
        nullable=False,
    )

    # Repost -> User
    user: Mapped["User"] = relationship(
        "User",
        back_populates="reposts",
    )

    # Repost -> Post
    post: Mapped["Post"] = relationship(
        "Post",
        back_populates="reposts",
    )
    
