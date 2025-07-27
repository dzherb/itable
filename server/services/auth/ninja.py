from typing import Iterable

from django.http import HttpRequest
from ninja.security import HttpBearer

from schemas.auth import AccessToken
from services.auth.service import authenticate_and_decode_token


class BearerAuth(HttpBearer):
    def __init__(self, required_scopes: Iterable[str] | None = None) -> None:
        if required_scopes is None:
            required_scopes = []

        self.required_scopes = required_scopes
        super().__init__()

    def authenticate(self, request: HttpRequest, token: str) -> AccessToken:
        # The result will be added to request.auth
        return authenticate_and_decode_token(self.required_scopes, token)
