
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ============================================================
# USER SCHEMAS
# ============================================================

class UserBase(BaseModel):
    username: str = Field(
        min_length=1,
        max_length=50,
    )

    email: EmailStr = Field(
        max_length=120,
    )


class UserCreate(UserBase):
    password: str = Field(
        min_length=8,
    )


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    image_file: str | None
    image_path: str


class UserPrivate(UserPublic):
    email: EmailStr


class UserUpdate(BaseModel):
    username: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
    )

    email: EmailStr | None = Field(
        default=None,
        max_length=120,
    )


# ============================================================
# AUTHENTICATION
# ============================================================

class Token(BaseModel):
    access_token: str
    token_type: str


# ============================================================
# POST SCHEMAS
# ============================================================

class PostCreate(BaseModel):
    """
    Data required when creating a new post.

    Image is NOT included here because the post must
    be created first before we have a post_id.
    """

    title: str = Field(
        min_length=1,
        max_length=100,
    )

    short_content: str = Field(
        min_length=1,
    )

    content: str = Field(
        min_length=1,
    )


class PostBase(BaseModel):
    """
    Common post fields returned by the API.
    """

    title: str = Field(
        min_length=1,
        max_length=100,
    )

    short_content: str = Field(
        min_length=1,
    )

    content: str = Field(
        min_length=1,
    )

    # image_file: str | None = None
    # image_path: str


class PostUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    content: str | None = Field(
        default=None,
        min_length=1,
    )


class PostResponse(PostBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    date_posted: datetime
    image_file: str | None = None
    image_path: str
    author: UserPublic

class PaginatedPostsResponse(BaseModel):
    posts: list[PostResponse]
    total: int
    skip: int
    limit: int
    has_more: bool


# ============================================================
# PASSWORD RESET
# ============================================================

class ForgotPasswordRequest(BaseModel):
    email: EmailStr = Field(
        max_length=120,
    )


class ResetPasswordRequest(BaseModel):
    token: str

    new_password: str = Field(
        min_length=8,
    )


class ChangePasswordRequest(BaseModel):
    current_password: str

    new_password: str = Field(
        min_length=8,
    )

class VerifyOtpRequest(BaseModel):
    email: EmailStr
    otp: str

class SendOtpRequest(BaseModel):
    username: str
    email: EmailStr
    password: str

