from collections.abc import Callable, Coroutine
import functools
import typing

from async_lru import alru_cache


class _AlwaysEquals:
    def __init__(self, original_object: typing.Any):
        self.original_object = original_object

    def __eq__(self, other: typing.Any) -> bool:
        return True

    def __hash__(self) -> int:
        return 0


class _ALRUCacheParams(typing.TypedDict):
    maxsize: int | None
    typed: bool
    ttl: float | None


class _AnyAsyncMethod[T](typing.Protocol):
    def __call__(
        self,
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> Coroutine[typing.Any, typing.Any, T]: ...


def alru_method_shared_cache[T](
    **kwargs: typing.Unpack[_ALRUCacheParams],
) -> Callable[[_AnyAsyncMethod[T]], _AnyAsyncMethod[T]]:
    """
    Wrapper for alru_cache that ignores "self" method argument.
    This way we can share cache between instances.
    """

    def decorator(fn: _AnyAsyncMethod[T]) -> _AnyAsyncMethod[T]:
        @alru_cache(**kwargs)
        async def helper(
            dummy_arg: _AlwaysEquals,
            *args: typing.Any,
            **kwargs: typing.Any,
        ) -> T:
            return await fn(dummy_arg.original_object, *args, **kwargs)

        @functools.wraps(fn)
        async def method(
            self: typing.Any,
            *args: typing.Any,
            **kwargs: typing.Any,
        ) -> T:
            return await helper(_AlwaysEquals(self), *args, **kwargs)

        return method

    return decorator
