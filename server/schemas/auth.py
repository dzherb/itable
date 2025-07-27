from typing import Literal

from pydantic import BaseModel, Field


class BaseToken(BaseModel):
    iat: float
    exp: float
    sub: str  # ID пользователя
    scopes: list[str]


class AccessToken(BaseToken):
    type: Literal['access']


class RefreshToken(BaseToken):
    type: Literal['refresh']


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class LoginCredentials(BaseModel):
    email: str = Field(min_length=1)
    password: str = Field(min_length=1)
    scopes: list[str] = Field(default_factory=list)


class RegisterCredentials(LoginCredentials):
    pass
