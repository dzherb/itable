import typing

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models

from users.authentication.jwt import JWT, PyJWT, TokenPair


class ItableUserManager(UserManager['ItableUser']):
    @typing.override
    def create_user(
        self,
        username: str | None = None,
        email: str | None = None,
        password: str | None = None,
        **extra_fields: typing.Any,
    ) -> 'ItableUser':
        return super().create_user(
            username,  # type: ignore[arg-type]
            email,
            password,
            **extra_fields,
        )

    @typing.override
    def create_superuser(
        self,
        username: str | None = None,
        email: str | None = None,
        password: str | None = None,
        **extra_fields: typing.Any,
    ) -> 'ItableUser':
        return super().create_superuser(
            username,  # type: ignore[arg-type]
            email,
            password,
            **extra_fields,
        )

    def _create_user(
        self,
        username: str | None,
        email: str | None,
        password: str | None,
        **extra_fields: typing.Any,
    ) -> 'ItableUser':
        assert email is not None
        assert password is not None
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user


class ItableUser(AbstractUser):
    username = None  # type: ignore[assignment]
    email = models.EmailField(unique=True, verbose_name='email', db_index=True)
    refresh_token = models.CharField(max_length=255, default='', blank=True)

    objects: typing.ClassVar[UserManager['ItableUser']] = ItableUserManager()

    USERNAME_FIELD: str = 'email'
    REQUIRED_FIELDS: typing.ClassVar[list[str]] = []

    JWT_FABRIC: JWT = PyJWT()

    def can_refresh_tokens(self, refresh_token: str) -> bool:
        return self.refresh_token == refresh_token

    async def generate_new_tokens(self) -> TokenPair:
        token_pair = self.JWT_FABRIC.generate_tokens(self.pk)
        await self._set_refresh_token(token_pair.refresh_token)
        return token_pair

    async def _set_refresh_token(self, refresh_token: str) -> None:
        self.refresh_token = refresh_token
        await self.asave(update_fields=['refresh_token'])
