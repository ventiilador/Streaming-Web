from pydantic import BaseModel, EmailStr, model_validator, field_validator
from datetime import datetime, timedelta

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