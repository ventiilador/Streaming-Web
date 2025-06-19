from typing import ClassVar, Literal
from pydantic import BaseModel, EmailStr, Field, model_validator, field_validator
from datetime import datetime, timedelta
from fastapi import Form

class UsernameForm(BaseModel):
    username: str

class VideoIdForm(BaseModel):
    id: int

class CommentForm(BaseModel):
    video_id: int
    content: str

    @field_validator("video_id")
    def video_id_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("video_id must be a positive integer")
        return v

    @field_validator("content")
    def content_must_not_be_empty(cls, v):
        v = v.strip()
        if len(v) == 0:
            raise ValueError("content must not be empty")
        if len(v) > 500:
            raise ValueError("content must be at most 500 characters")
        return v

class GetCommentsForm(BaseModel):
    video_id: int
    offset: int
    order_by: str

class LikeComment(BaseModel):
    comment_id: int


class LoginForm(BaseModel):
    username: str
    password: str

    @classmethod
    def as_form(
        cls,
        username: str = Form(...),
        password: str = Form(...)
    ):
        return cls(username=username, password=password)

    @field_validator("username")
    def username_range(cls, v):
        if not v:
            raise ValueError("Username cannot be empty")
        if len(v) > 20:
            raise ValueError("Username max length: 20")
        return v

    @field_validator("password")
    def password_range(cls, v):
        if not v:
            raise ValueError("Password cannot be empty")
        if len(v) > 64:
            raise ValueError("Password max length: 64")
        return v


class RegisterForm(BaseModel):
    username: str
    email: EmailStr
    password: str

    @classmethod
    def as_form(
        cls,
        username: str = Form(...),
        email: EmailStr = Form(...),
        password: str = Form(...)
    ):
        return cls(username=username, email=email, password=password)

    @field_validator("username")
    def username_range(cls, v):
        if not v:
            raise ValueError("Username cannot be empty")
        if " " in v:
            raise ValueError("Username cannot have empty spaces")
        if not 4 <= len(v) <= 20:
            raise ValueError("Username must be between 4 and 20 chars")
        return v

    @field_validator("email")
    def email_range(cls, v):
        if not v:
            raise ValueError("Email cannot be empty")
        if " " in v:
            raise ValueError("Email cannot have empty spaces")
        if not 6 <= len(v) <= 254:
            raise ValueError("Email must be between 6 and 254 chars")
        return v

    @field_validator("password")
    def password_range(cls, v):
        if not v:
            raise ValueError("Password cannot be empty")
        if " " in v:
            raise ValueError("Password cannot have empty spaces")
        if not 8 <= len(v) <= 64:
            raise ValueError("Password must be between 8 and 64 chars")
        return v


class EditVideoForm(BaseModel):
    id: int
    title: str
    description: str

    @classmethod
    def as_form(
        cls,
        id: int = Form(...),
        title: str = Form(...),
        description: str = Form(...)
    ):
        return cls(id=id, title=title, description=description)

    @field_validator("title")
    def validate_title(cls, v):
        if not 4 <= len(v) <= 24:
            raise ValueError("Title must be between 4 and 24 characters.")
        return v

    @field_validator("description")
    def validate_description(cls, v):
        if not 5 <= len(v) <= 400:
            raise ValueError("Description must be between 5 and 400 characters.")
        return v

class UpdateProfileForm(BaseModel):
    username: str
    biography: str

    @classmethod
    def as_form(
        cls,
        username: str = Form(...),
        biography: str = Form(...)
    ):
        return cls(username=username, biography=biography)

    @field_validator("username")
    def validate_username(cls, v):
        if " " in v:
            raise ValueError("Username cannot contain spaces")
        if not 4 <= len(v) <= 20:
            raise ValueError("Username must be between 4 and 20 characters")
        return v

    @field_validator("biography")
    def validate_biography(cls, v):
        if len(v.strip()) > 40:
            raise ValueError("Biography must be at most 40 characters")
        return v.strip()
    


class SearchForm(BaseModel):
    search: str = Field(..., min_length=1, max_length=100)
    filter: Literal["recent", "oldest", "popular", "relevance"]
    type: Literal["videos", "channels"]
    offset: int = Field(0, ge=0)

    allowed_filters: ClassVar[set[str]] = {"recent", "oldest", "popular", "relevance"}

    @classmethod
    def as_form(
        cls,
        search: str = Form(..., min_length=1, max_length=100),
        filter: Literal["recent", "oldest", "popular", "relevance"] = Form(...),
        type: Literal["videos", "channels"] = Form(...),
        offset: int = Form(0),
    ):
        return cls(search=search, filter=filter, type=type, offset=offset)