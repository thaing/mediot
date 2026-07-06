from typing import Literal

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr
    social_provider: Literal["google", "apple", "facebook"]


class UserOut(BaseModel):
    id: int
    first_name: str | None = None
    last_name: str | None = None
    email: str
    social_provider: str
    created_at: str | None = None

    class Config:
        from_attributes = True
